import re
import logging
import PyPDF2
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import unicodedata
import regex


# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass(frozen=True)
class Citation:
    """Classe représentant une citation"""

    text: str
    authors: str
    year: str
    page: int


@dataclass
class Reference:
    """Représente une référence bibliographique"""

    authors: str
    year: str
    title: str
    revue: str
    raw_text: str

    def __str__(self) -> str:
        return f"{self.authors} ({self.year}). {self.title}. {self.revue}"


class PDFTextExtractor:
    """Classe pour extraire le texte d'un PDF"""

    @staticmethod
    def extract(file_path: Path) -> Tuple[str, Dict[int, Dict[str, str]]]:
        """Extrait le texte complet d'un fichier PDF et retourne également les premières et dernières lignes de chaque page"""
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text_pages = []
                page_lines = {}

                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            lines = text.split("\n")
                            text_pages.append((page_num, text))
                            # Stocker les premières et dernières lignes de la page
                            if lines:
                                page_lines[page_num] = {
                                    "first_line": lines[0].strip(),
                                    "last_line": lines[-1].strip(),
                                }
                    except Exception as e:
                        logging.warning(
                            f"Erreur lors de l'extraction de la page {page_num}: {e}"
                        )

                full_text = "\n".join(
                    f"<PAGE_{num}>\n{text}\n</PAGE_{num}>" for num, text in text_pages
                )
                return full_text, page_lines
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du PDF: {e}")
            raise


def preprocess_text(text: str) -> str:
    """
    Prétraite le texte des références pour unifier les lignes cassées
    et garder la structure des références.
    """
    # Normaliser les caractères Unicode
    text = unicodedata.normalize("NFKC", text)

    # Supprimer les tirets en fin de ligne et joindre les mots cassés
    text = re.sub(r"-\n", "", text)
    text = re.sub(r'\s,\s', ', ', text)
    text = re.sub(r'\s\.\s', '. ', text)

    # Supprimer les retours à la ligne à l'intérieur des phrases (sauf après un point)
    text = re.sub(r"(?<!\.)\n", " ", text)

    # Supprimer les marqueurs de page
    text = re.sub(r"<PAGE_\d+>", "", text)
    text = re.sub(r"</PAGE_\d+>", "", text)

    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text)

    # Ajouter un retour à la ligne avant les sections de références
    text = re.sub(r"\.\s*(References|Bibliography)\s", ".\nReferences\n", text)

    # Ajouter un retour à la ligne après des patterns spécifiques (e.g., "6(2):220–236.")
    text = re.sub(r"(\d+\(\d+\):\d+(?:–|-)\d+\.)", r"\1\n", text)
    # Ajouter un retour à la ligne après les références terminées par un point suivi d'une majuscule
    text = re.sub(r"(?<=[a-zA-Z]\.)(\s+)(?=[A-Z])", r"\n", text)

    # Fusionner les lignes cassées qui appartiennent à la même référence
    lines = text.strip().split("\n")
    processed_lines = []
    current_line = ""

    for line in lines:
        line = line.strip()
        # Détecter le début d'une nouvelle référence
        if re.match(r"^[A-Z][A-Za-zÀ-ÖØ-öø-ÿ\'\-\.]+(?:,| and)", line):
            if current_line:
                processed_lines.append(current_line.strip())
            current_line = line
        else:
            current_line += " " + line

    if current_line:
        processed_lines.append(current_line.strip())

    # Retourner les références prétraitées
    return "\n".join(processed_lines)


def identify_repeated_lines(page_lines: Dict[int, Dict[str, str]]) -> Set[str]:
    """Identifie les lignes qui se répètent fréquemment en haut ou en bas des pages"""
    first_lines = [info["first_line"] for info in page_lines.values()]
    last_lines = [info["last_line"] for info in page_lines.values()]
    all_lines = first_lines + last_lines

    line_counts = {}
    for line in all_lines:
        if line in line_counts:
            line_counts[line] += 1
        else:
            line_counts[line] = 1

    # Seuil pour déterminer si une ligne est récurrente (par exemple, apparaît sur plus de 50% des pages)
    threshold = len(page_lines) * 0.5
    repeated_lines = {line for line, count in line_counts.items() if count > threshold}

    return repeated_lines


class CitationExtractor:
    """Classe pour extraire les citations d'un texte académique"""

    def __init__(self, ignored_lines: Set[str] = None):
        self.ignored_lines = ignored_lines or set()

    def extract(self, text: str) -> List[Citation]:
        """Extrait toutes les citations du texte"""
        citations = set()
        current_page = 1

        # Traitement ligne par ligne
        for line in text.split("\n"):
            # Détection des marqueurs de page
            page_match = re.match(r"<PAGE_(\d+)>", line)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            # Nettoyage et normalisation
            line = self._clean_text(line)

            # Ignorer les lignes récurrentes (en-têtes et pieds de page)
            if line in self.ignored_lines:
                continue

            # Extraction des citations entre parenthèses
            parenthetical_citations = re.findall(r"\(([^()]+)\)", line)
            for citation_text in parenthetical_citations:
                # Split multiple citations
                for sub_citation in citation_text.split(";"):
                    sub_citation = sub_citation.strip()
                    parsed_citation = self._parse_single_citation(
                        sub_citation, current_page
                    )
                    if parsed_citation:
                        citations.add(parsed_citation)

            # Recherche des citations intégrées au texte
            in_text_pattern = (
                r"(?P<authors>[A-Z][a-zA-Z\s\.-]+?)\s*\((?P<year>\d{4}[a-z]?)\)"
            )
            matches = re.finditer(in_text_pattern, line)
            for match in matches:
                authors = match.group("authors").strip()
                year = match.group("year").strip()
                citation_text = match.group(0)
                citations.add(
                    Citation(
                        text=citation_text,
                        authors=authors,
                        year=year,
                        page=current_page,
                    )
                )

        # Après avoir collecté les citations, filtrer les faux positifs
        citations = [c for c in citations if not self._is_false_positive(c)]
        return sorted(citations, key=lambda c: (c.year, c.authors))

    def _clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        # Normalisation des espaces
        text = " ".join(text.split())

        # Normalisation des caractères spéciaux
        replacements = {
            "'": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "é": "e",
            "è": "e",
            "’": "'",
            "‐": "-",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def _parse_single_citation(self, text: str, page: int) -> Optional[Citation]:
        """Parse une citation individuelle"""
        # Nettoyage initial
        text = text.strip()

        # Extraction de l'année
        year_match = re.search(r"(\d{4}[a-z]?)", text)
        if not year_match:
            return None

        year = year_match.group(1)

        # Extraction des auteurs
        authors_part = text.split(year)[0].strip(" ,")

        # Nettoyage final des auteurs
        authors = re.sub(r",\s*(?:Appendix|p\.)\s*[0-9\.-]+", "", authors_part)
        authors = authors.strip(" ,")

        # Vérification de la validité
        if not authors or not re.search(r"[A-Za-z]", authors):
            return None

        return Citation(text=text, authors=authors, year=year, page=page)

    def _is_false_positive(self, citation: Citation) -> bool:
        """Vérifie si une citation est un faux positif basé sur des auteurs non pertinents"""
        false_positives = {"NLP4CALL", "SLAM shared task. Kim"}
        return citation.authors in false_positives


class ReferenceExtractor:
    """Classe améliorée pour extraire les références bibliographiques"""

    def __init__(self):
        # Ajout de marqueurs supplémentaires pour détecter la section des références
        self.ref_section_markers = [
            "References",
        ]
        self.ref_patterns = [
            r"^[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)+(?:,\s(?:and\s)?[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)*)?\.", # Mitchell, T. M., Mabadevan, S., and Steinberg, L.
            r"^[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)+(?:,\s[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)*)*", # Lehman, C. D., Arao, R. F., ...
            r"^[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)+,\sand\s[A-Za-z]{2,}(?:,?\s[A-Z]\.?(?:\s[A-Z]\.?)?)*\.", # Lazarus, E., Mainie ro, M. B., and Livingston, L.
        ]
        
        self.ref_pattern2 = [r"^[\w,\sÀ-ÖØ-öø-ÿ\s]+(?:and [\w,À-ÖØ-öø-ÿ\s]+)*\."]

    def extract(self, text: str) -> List[str]:
        references = []
        ref_section_text = ""
        in_ref_section = False

        # Récupérer le texte de la section des références
        lines = text.split("\n")
        for line in lines:
            normalized_line = re.sub(r"\s+", " ", line.strip())
            if re.search(r"\bReferences\b", normalized_line):
                in_ref_section = True
                normalized_line = normalized_line.split("References", 1)[-1].strip()
                print("Début de la section Références")

            # Arrêter l'ajout si "About the Authors" est détecté
            if re.search(r"\bAbout the A\s?uthors\b", normalized_line, re.IGNORECASE):
                print("Fin de la section Références détectée")
                in_ref_section = False
                break

            if in_ref_section:
                if not self._is_ignorable_line(normalized_line):
                    ref_section_text += " " + normalized_line
                else:
                    print(f"Ligne ignorée : {normalized_line}")

        if ref_section_text:
            reference = []
            # Splitter le texte par point tout en conservant les points
            segments = re.split(r"(?<=\.)\s+", ref_section_text.strip())
            # segments = re.findall(r"\s[A-Za-z]{2,}\.\s+|[^.]+", ref_section_text.strip())
            print(f"segments : {segments}")

            for i in range(len(segments)):
                seg = segments[i]
                seg = seg.strip()  # Nettoyer chaque segment
                next_seg = segments[i + 1] if i + 1 < len(segments) else ""
                print(f"seg : {seg}")

                # Détecter le début d'une nouvelle référence
                if (
                    any(
                        re.match(pattern, seg, re.UNICODE)
                        for pattern in self.ref_pattern2
                    )
                    and (re.match(r"\d{4}.", next_seg))
                ) or any(
                    re.match(pattern, seg, re.UNICODE) for pattern in self.ref_patterns
                ):
                    print(f"New reference : {seg}")
                    # Ajouter la référence précédente si elle existe
                    if reference:
                        references.append(" ".join(reference).strip())
                        reference = []

                    # Commencer une nouvelle référence
                    reference.append(seg)
                else:
                    # Continuer la référence actuelle
                    if reference:
                        reference.append(seg)

            # Ajouter la dernière référence si elle existe
            if reference:
                references.append(" ".join(reference).strip())

        return references

    def _is_ignorable_line(self, line: str) -> bool:
        """Vérifie si une ligne doit être ignorée"""
        return line.startswith("<PAGE_") or line.isdigit()

    def _clean_reference(self, text: str) -> str:
        """Nettoie et normalise une référence"""
        # Normaliser les caractères Unicode
        text = unicodedata.normalize("NFKC", text)
        text = text.encode("ascii", "ignore").decode("ascii")

        # Suppression des espaces multiples
        text = " ".join(text.split())

        # Nettoyage des caractères spéciaux
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r"\s+\.", ".", text)
        text = re.sub(r"\s+\)", ")", text)
        text = re.sub(r"\(\s+", "(", text)

        # Vérification de la validité minimale
        if len(text) < 20 or not re.search(r"\d{4}", text):
            return ""

        return text


def process_academic_paper(file_path: str) -> Tuple[List[Citation], List[str]]:
    """Fonction principale de traitement d'un article académique"""
    file_path = Path(file_path)

    # Extraction du texte et des lignes par page
    logging.info(f"Lecture du fichier: {file_path}")
    text, page_lines = PDFTextExtractor.extract(file_path)

    # Prétraiter le texte pour l'extraction des références
    preprocessed_text = preprocess_text(text)
    # print(preprocessed_text)

    # Identifier les lignes récurrentes (en-têtes et pieds de page)
    logging.info("Identification des en-têtes et pieds de page récurrents...")
    repeated_lines = identify_repeated_lines(page_lines)
    logging.info(f"Lignes récurrentes identifiées: {repeated_lines}")

    # Extraction des citations
    logging.info("Extraction des citations...")
    citation_extractor = CitationExtractor(ignored_lines=repeated_lines)
    citations = citation_extractor.extract(text)
    logging.info(f"Nombre de citations trouvées: {len(citations)}")

    # Extraction des références
    logging.info("Extraction des références...")
    reference_extractor = ReferenceExtractor()
    references = reference_extractor.extract(preprocessed_text)
    logging.info(f"Nombre de références trouvées: {len(references)}")

    return citations, references


def main():
    """Point d'entrée du script"""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 parsing_extraction.py <chemin_du_fichier_pdf>")
        sys.exit(1)

    try:
        citations, references = process_academic_paper(sys.argv[1])

        print("\nCitations trouvées:")
        for i, citation in enumerate(citations, 1):
            print(f"{i}. {citation}")

        print("\nRéférences trouvées:")
        for i, ref in enumerate(references, 1):
            print(f"{i}. {ref}")

    except Exception as e:
        logging.error(f"Erreur lors du traitement: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
