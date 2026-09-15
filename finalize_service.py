from datetime import datetime

with open("notice_of_appeal.md", "r", encoding="utf-8") as f:
    text = f.read()

# Fill service date and details
today_str = datetime.now().strftime("%B %d, %Y")
text = text.replace(
    "I certify that on **____________________**",
    f"I certify that on **{today_str}**",
)
text = text.replace(
    "using **____________________**",
    "using **Supreme Court of Ohio E-Filing Portal / Electronic Service**",
)
text = text.replace(
    "Name: __________________________________________",
    "Name: Brandon J. Waltenbaugh / Christina G. Eoff, Esqs.",
)
text = text.replace(
    "Address: ________________________________________  \n________________________________________________",
    "Address: 402 2nd St. SE, Canton, OH 44702",
)
text = text.replace("Date: ____________________", f"Date: {today_str}")

with open("notice_of_appeal.md", "w", encoding="utf-8") as f:
    f.write(text)

print("[+] Service block populated.")
