import csv
import json
from connect import get_connection


def run_sql_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        sql = file.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def setup_database():
    run_sql_file("schema.sql")
    run_sql_file("procedures.sql")
    print("Database is ready.")


def get_group_id(cur, group_name):
    cur.execute(
        "INSERT INTO groups(name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
        (group_name,)
    )
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    return cur.fetchone()[0]


def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday YYYY-MM-DD: ")
    group_name = input("Group: ")
    phone = input("Phone: ")
    phone_type = input("Phone type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()

    group_id = get_group_id(cur, group_name)

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (name)
        DO UPDATE SET email = EXCLUDED.email,
                      birthday = EXCLUDED.birthday,
                      group_id = EXCLUDED.group_id
        RETURNING id
    """, (name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s, %s, %s)
    """, (contact_id, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()
    print("Contact saved.")


def add_phone_to_contact():
    name = input("Contact name: ")
    phone = input("New phone: ")
    phone_type = input("Phone type home/work/mobile: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
    conn.commit()
    cur.close()
    conn.close()
    print("Phone added.")


def move_contact_to_group():
    name = input("Contact name: ")
    group_name = input("New group: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL move_to_group(%s, %s)", (name, group_name))
    conn.commit()
    cur.close()
    conn.close()
    print("Contact moved.")


def print_rows(rows):
    if not rows:
        print("No results.")
        return

    for row in rows:
        print("-" * 40)
        print("Name:", row[0])
        print("Email:", row[1])
        print("Birthday:", row[2])
        print("Group:", row[3])
        print("Phone:", row[4])
        print("Type:", row[5])


def filter_by_group():
    group_name = input("Group name: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name ILIKE %s
        ORDER BY c.name
    """, (group_name,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def search_by_email():
    text = input("Email search text: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.email ILIKE %s
        ORDER BY c.name
    """, ("%" + text + "%",))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def search_all_fields():
    text = input("Search text: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (text,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def list_sorted_contacts():
    print("Sort by: name / birthday / date")
    sort_by = input("Choose: ")

    if sort_by == "birthday":
        order_column = "c.birthday"
    elif sort_by == "date":
        order_column = "c.date_added"
    else:
        order_column = "c.name"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY {order_column}
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def pagination_menu():
    limit = 3
    offset = 0

    while True:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        print("\nPage:", offset // limit + 1)
        print_rows(rows)

        command = input("next / prev / quit: ")

        if command == "next":
            offset += limit
        elif command == "prev":
            offset = max(0, offset - limit)
        elif command == "quit":
            break
        else:
            print("Wrong command.")


def export_to_json():
    filename = input("Output file name, example contacts.json: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.name
    """)

    contacts = []

    for contact_id, name, email, birthday, group_name in cur.fetchall():
        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
        """, (contact_id,))

        phones = []
        for phone, phone_type in cur.fetchall():
            phones.append({
                "phone": phone,
                "type": phone_type
            })

        contacts.append({
            "name": name,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": phones
        })

    cur.close()
    conn.close()

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)

    print("Exported to", filename)


def save_contact_from_dict(cur, item, overwrite):
    name = item["name"]
    email = item.get("email")
    birthday = item.get("birthday")
    group_name = item.get("group", "Other")
    phones = item.get("phones", [])

    group_id = get_group_id(cur, group_name)

    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
    old_contact = cur.fetchone()

    if old_contact and not overwrite:
        return "skipped"

    if old_contact and overwrite:
        contact_id = old_contact[0]
        cur.execute("""
            UPDATE contacts
            SET email = %s, birthday = %s, group_id = %s
            WHERE id = %s
        """, (email, birthday, group_id, contact_id))
        cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
    else:
        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email, birthday, group_id))
        contact_id = cur.fetchone()[0]

    for phone_item in phones:
        cur.execute("""
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
        """, (contact_id, phone_item["phone"], phone_item["type"]))

    return "saved"


def import_from_json():
    filename = input("JSON file name: ")

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = get_connection()
    cur = conn.cursor()

    for item in data:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (item["name"],))
        exists = cur.fetchone()

        overwrite = True
        if exists:
            answer = input(f"{item['name']} exists. skip or overwrite? ")
            overwrite = answer == "overwrite"

        result = save_contact_from_dict(cur, item, overwrite)
        print(item["name"], result)

    conn.commit()
    cur.close()
    conn.close()


def import_from_csv():
    filename = input("CSV file name: ")

    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            item = {
                "name": row["name"],
                "email": row["email"],
                "birthday": row["birthday"],
                "group": row["group"],
                "phones": [
                    {
                        "phone": row["phone"],
                        "type": row["type"]
                    }
                ]
            }

            save_contact_from_dict(cur, item, overwrite=True)

    conn.commit()
    cur.close()
    conn.close()
    print("CSV imported.")


def menu():
    while True:
        print("\nPHONEBOOK MENU")
        print("1. Setup database")
        print("2. Add contact")
        print("3. Add phone to contact")
        print("4. Move contact to group")
        print("5. Filter by group")
        print("6. Search by email")
        print("7. Search all fields")
        print("8. List sorted contacts")
        print("9. Pagination")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            setup_database()
        elif choice == "2":
            add_contact()
        elif choice == "3":
            add_phone_to_contact()
        elif choice == "4":
            move_contact_to_group()
        elif choice == "5":
            filter_by_group()
        elif choice == "6":
            search_by_email()
        elif choice == "7":
            search_all_fields()
        elif choice == "8":
            list_sorted_contacts()
        elif choice == "9":
            pagination_menu()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            import_from_csv()
        elif choice == "0":
            break
        else:
            print("Wrong choice.")


menu()
