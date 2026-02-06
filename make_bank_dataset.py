import random

def money(x):  # format rupees
    return f"₹{x:,}"

def pct(x):
    return f"{x:.2f}%"

random.seed(7)

bank = "ABC Bank"  # you can rename

# --- Core facts (you can edit these numbers) ---
facts = {
    "savings_min_balance": 2000,
    "savings_interest": 3.00,
    "current_min_balance": 5000,
    "home_loan_rate": 8.50,
    "car_loan_rate": 9.20,
    "gold_loan_rate": 10.50,
    "personal_loan_rate": 12.75,
    "education_loan_rate": 9.75,
    "fd_rate": 7.10,
    "rd_rate": 6.90,
    "upi_limit": 100000,
    "atm_withdrawal_limit": 20000,
    "imps_limit": 200000,
    "neft_limit": 500000,
    "rtgs_limit_min": 200000,
    "customer_care": "1800-123-456",
    "email": "support@abcbank.in",
}

# --- Templates: many paraphrases for same info (helps embeddings) ---
templates = []

# Savings account
templates += [
    f"{bank} savings account minimum balance is {money(facts['savings_min_balance'])}.",
    f"Minimum balance required for savings account is {money(facts['savings_min_balance'])}.",
    f"To avoid charges, keep at least {money(facts['savings_min_balance'])} in savings account.",
    f"Savings account interest rate is around {pct(facts['savings_interest'])} per annum.",
]

# Current account
templates += [
    f"Current account minimum balance is {money(facts['current_min_balance'])}.",
    f"For current account, maintain {money(facts['current_min_balance'])} minimum balance.",
]

# Loans
templates += [
    f"Home loan interest rate starts from {pct(facts['home_loan_rate'])}.",
    f"Car loan interest rate starts from {pct(facts['car_loan_rate'])}.",
    f"Vehicle loan interest is about {pct(facts['car_loan_rate'])}.",
    f"Gold loan interest rate starts from {pct(facts['gold_loan_rate'])}.",
    f"Personal loan interest rate starts from {pct(facts['personal_loan_rate'])}.",
    f"Education loan interest rate starts from {pct(facts['education_loan_rate'])}.",
]

# Deposits
templates += [
    f"Fixed deposit (FD) interest rate is up to {pct(facts['fd_rate'])} depending on tenure.",
    f"Recurring deposit (RD) interest rate is up to {pct(facts['rd_rate'])} depending on tenure.",
]

# Limits
templates += [
    f"UPI transaction limit per day is {money(facts['upi_limit'])}.",
    f"ATM cash withdrawal limit per day is {money(facts['atm_withdrawal_limit'])}.",
    f"IMPS transfer limit is {money(facts['imps_limit'])}.",
    f"NEFT transfer limit is {money(facts['neft_limit'])}.",
    f"RTGS minimum transfer amount is {money(facts['rtgs_limit_min'])}.",
]

# Support
templates += [
    f"Customer care number is {facts['customer_care']}.",
    f"Contact {bank} support at {facts['customer_care']}.",
    f"Support email is {facts['email']}.",
]

# Add many “FAQ-style” variations
faq_topics = [
    ("how to open account", "You can open an account through the mobile app or by visiting the nearest branch with KYC documents."),
    ("kyc documents", "KYC documents include Aadhaar, PAN, and address proof. Passport/Voter ID can also be used."),
    ("debit card block", "To block your debit card, use the mobile app or call customer care immediately."),
    ("net banking registration", "Register net banking using your account number, registered mobile number, and OTP."),
    ("upi pin reset", "You can reset UPI PIN in your UPI app using debit card details and OTP."),
    ("forgot atm pin", "If you forgot ATM PIN, generate a new PIN from the app or ATM PIN services."),
    ("close account", "To close an account, visit the branch with ID proof and submit closure request."),
    ("cheque book", "Cheque book request is available in the app under Services → Cheque Book."),
    ("stop cheque", "Stop cheque can be done via app or branch by providing cheque number and account details."),
    ("loan eligibility", "Loan eligibility depends on income, credit score, age, and repayment capacity."),
    ("credit score", "A higher credit score improves loan approval chances and can reduce interest rate."),
    ("emi calculation", "EMI depends on principal, interest rate, and tenure. Use an EMI calculator for exact value."),
    ("foreclosure charges", "Foreclosure charges depend on loan type and terms. Check loan agreement for details."),
    ("branch timings", "Branch timing is typically 9:30 AM to 4:00 PM on working days (may vary by location)."),
]

# Expand to large dataset
lines = []
lines.extend(templates)

# Create 500+ lines by random paraphrases
paraphrase_starts = [
    "Info:", "Note:", "FAQ:", "Details:", "Answer:", "For customers:", "As per policy:",
    "In general:", "Usually:", "Quick help:"
]
for _ in range(700):  # increase if you want bigger
    t = random.choice(templates)
    prefix = random.choice(paraphrase_starts)
    lines.append(f"{prefix} {t}")

# Add FAQ topics with many variations
for topic, ans in faq_topics:
    for _ in range(25):
        qstyle = random.choice([
            f"{topic}?",
            f"Can you explain {topic}?",
            f"I want to know {topic}.",
            f"Tell me about {topic}.",
            f"How to do {topic} in {bank}?",
        ])
        lines.append(f"Q: {qstyle} A: {ans}")

# Remove duplicates and write
lines = list(dict.fromkeys(lines))

with open("bank_data_large.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line.strip() + "\n")

print(f"✅ Created bank_data_large.txt with {len(lines)} lines")
