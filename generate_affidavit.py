affidavit_text = """# IN THE SUPREME COURT OF OHIO

AFFIDAVIT OF INDIGENCE

I, Dwayne Jones, do hereby solemnly swear that I am without the necessary funds to pay the costs of this action for the following reason(s):

1. I am currently without sufficient income or liquid assets to pay the required $100.00 docket fee or security deposit for this jurisdictional appeal.
2. My current financial situation prevents me from paying court costs without creating a severe financial hardship for myself and my family.

Pursuant to Rule 3.06 of the Rules of Practice of the Supreme Court of Ohio, I am requesting that the filing fee and security deposit, if applicable, be waived.

__________________________________________
Dwayne Jones, Affiant / Pro Se Appellant
120 E 44 Street Chicago IL 60653 Apt 2E

Sworn to, or affirmed, and subscribed in my presence this ____ day of ______________, 2026.

__________________________________________
Notary Public
My Commission Expires: ____________________
"""

with open("AFFIDAVIT_OF_INDIGENCE.md", "w", encoding="utf-8") as f:
    f.write(affidavit_text)

print("[+] AFFIDAVIT_OF_INDIGENCE.md created successfully.")
