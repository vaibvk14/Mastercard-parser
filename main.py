import os

# --- 1. MOCK MDES VAULT (Tokenization Database) ---
mdes_vault = {
    "4000123456789010": "5412751234567890" 
}

# --- 2. THE PARSER LOGIC ---
def parse_legacy_auth(raw_message):
    parsed_data = {
        "message_type": "0100", 
        "DE_02_PAN": raw_message[4:20], 
        "DE_04_Amount": raw_message[20:32], 
        "DE_22_EntryMode": raw_message[32:34] 
    }
    print(f"Parsed ISO 8583 Message: {parsed_data['DE_04_Amount']} from card ending in {parsed_data['DE_02_PAN'][-4:]}")
    return parsed_data

# --- 3. THE TOKEN RESOLVER LOGIC ---
def resolve_token(pan, entry_mode):
    if entry_mode == '07':
        print("Tokenized transaction detected. Querying MDES vault...")
        real_fpan = mdes_vault.get(pan, "Token Not Found")
        masked_fpan = f"XXXX-XXXX-XXXX-{real_fpan[-4:]}"
        return masked_fpan
    else:
        print("Standard physical card transaction.")
        return f"XXXX-XXXX-XXXX-{pan[-4:]}"

# --- 4. THE FRAUD ENGINE & REMINDERS INTEGRATION ---
def flag_for_review(amount, masked_pan):
    print("High risk detected! Sending to Apple Reminders for manual review...")
    reminder_text = f"Review High-Risk Transaction: ${amount} on card {masked_pan}"
    os.system(f"osascript -e 'tell application \"Reminders\" to make new reminder with properties {{name:\"{reminder_text}\"}}'")
    print("Reminder successfully created.")

# --- 5. THE MAIN ORCHESTRATOR ---
def run_payment_pipeline():
    # Simulated incoming Apple Pay transaction for $500.00
    raw_payload = "0100400012345678901000000005000007"
    
    parsed_txn = parse_legacy_auth(raw_payload)
    secure_pan = resolve_token(parsed_txn["DE_02_PAN"], parsed_txn["DE_22_EntryMode"])
    print(f"Transaction secured. Final PAN: {secure_pan}")
    
    amount_in_dollars = int(parsed_txn["DE_04_Amount"]) / 100
    if amount_in_dollars > 400:
        flag_for_review(amount_in_dollars, secure_pan)

if __name__ == "__main__":
    run_payment_pipeline()
