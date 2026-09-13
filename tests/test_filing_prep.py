import os
import tempfile
import unittest

import main


class FilingPrepTests(unittest.TestCase):
    def test_update_markdown_source_replaces_date_and_gal_block(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "appellate_brief.md")
            source_text = """
# Test

I hereby certify this day of ___, 20___.

**Atty DeRamus, Esq.**
Guardian ad Litem for the Minor Children
"""
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(source_text)

            original_source = main.SOURCE_MD
            original_pdf = main.OFFICIAL_PDF
            original_target = main.TARGET_PDF
            try:
                main.SOURCE_MD = source_path
                main.OFFICIAL_PDF = os.path.join(tmpdir, "Golden eye.pdf")
                main.TARGET_PDF = os.path.join(tmpdir, "FINAL_SUPREME_COURT_MEMORANDUM.pdf")
                main.BACKUP_DIR = os.path.join(tmpdir, "filing_backups")

                ok = main.update_markdown_source()
                self.assertTrue(ok)

                with open(source_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("this 2nd day of September, 2026", content)
                self.assertIn("Atty DeRamus, Esq.", content)
                self.assertIn("Guardian ad Litem for the Minor Children", content)
                self.assertNotIn("___", content)
            finally:
                main.SOURCE_MD = original_source
                main.OFFICIAL_PDF = original_pdf
                main.TARGET_PDF = original_target
                main.BACKUP_DIR = original_source.rsplit("/", 1)[0] if "/" in original_source else ""


if __name__ == "__main__":
    unittest.main()
