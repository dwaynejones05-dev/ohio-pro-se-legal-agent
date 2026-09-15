with open("notice_of_appeal.md", "r") as f:
    text = f.read()

    # Fix incorrect court references and grammar
    text = text.replace(
        "On Appeal from the Stark County Family Court / Juvenile Division",
        "On Appeal from the Stark County Court of Appeals, Fifth Appellate District",
    )
    text = text.replace(
        "appeals to the\n**Fifth Appellate District**",
        "appeals to the\n**Supreme Court of Ohio**",
    )
    text = text.replace(
        "in the\n**Stark County Family Court / Juvenile Division**",
        "in the\n**Court of Appeals, Fifth Appellate District, Stark County, Ohio**",
    )
    text = text.replace(
        "**Reversal of the Fifth District Court of Appeals decision and acceptance of jurisdiction by the Supreme Court of Ohio**",
        "**reverse the decision of the Fifth District Court of Appeals and accept jurisdiction in this matter**",
    )
    text = text.replace(
        "**September 5, 2026**",
        "**September 21, 2026**",
    )

with open("notice_of_appeal.md", "w") as f:
    f.write(text)

print("[+] notice_of_appeal.md updated successfully.")