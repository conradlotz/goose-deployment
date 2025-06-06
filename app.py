import json
import os
from datetime import datetime
import re


class Contact:
    def __init__(self, name, phone, email, notes=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.notes = notes
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'notes': self.notes,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        contact = cls(data['name'], data['phone'], data['email'], data.get('notes', ''))
        contact.created_at = data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return contact
    
    def __str__(self):
        return f"📞 {self.name} | {self.phone} | {self.email}"


class ContactManager:
    #comment
    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = []
        self.load_contacts()
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        # Simple phone validation - digits, spaces, dashes, parentheses
        pattern = r'^[\d\s\-\(\)\+]+$'
        return re.match(pattern, phone) is not None and len(re.sub(r'[\s\-\(\)\+]', '', phone)) >= 10
    
    def add_contact(self):
        print("\n➕ Add New Contact")
        name = input("Name: ").strip()
        phone = input("Phone: ").strip()
        email = input("Email: ").strip()
        notes = input("Notes (optional): ").strip()

        if not name:
            success, message = False, "Name cannot be empty"
        elif not self.validate_phone(phone):
            success, message = False, "Invalid phone number format"
        elif not self.validate_email(email):
            success, message = False, "Invalid email format"
        elif any(c.email.lower() == email.lower() for c in self.contacts):
            success, message = False, "Contact with this email already exists"
        else:
            contact = Contact(name, phone, email, notes)
            self.contacts.append(contact)
            self.save_contacts()
            success, message = True, "Contact added successfully"
        
        print(f"{'✅' if success else '❌'} {message}")
    
    def search_contacts(self, query):
        query = query.lower()
        results = []
        for contact in self.contacts:
            if (query in contact.name.lower() or 
                query in contact.phone or 
                query in contact.email.lower() or 
                query in contact.notes.lower()):
                results.append(contact)
        return results
    
    def find_contact_by_email(self, email):
        for contact in self.contacts:
            if contact.email.lower() == email.lower():
                return contact
        return None
    
    def delete_contact(self, email):
        for i, contact in enumerate(self.contacts):
            if contact.email.lower() == email.lower():
                deleted = self.contacts.pop(i)
                self.save_contacts()
                return True, f"Deleted contact: {deleted.name}"
        return False, "Contact not found"
    
    def get_all_contacts(self):
        return sorted(self.contacts, key=lambda x: x.name.lower())
    
    def save_contacts(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump([contact.to_dict() for contact in self.contacts], f, indent=2)
        except Exception as e:
            print(f"Error saving contacts: {e}")
    
    def load_contacts(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.contacts = [Contact.from_dict(item) for item in data]
            except Exception as e:
                print(f"Error loading contacts: {e}")
                self.contacts = []


def display_menu():
    print("\n" + "="*50)
    print("📱 CONTACT MANAGER")
    print("="*50)
    print("1. Add Contact")
    print("2. View All Contacts")
    print("3. Search Contacts")
    print("4. Delete Contact")
    print("5. Contact Statistics")
    print("6. Exit")
    print("="*50)


def display_contacts(contacts):
    if not contacts:
        print("📭 No contacts found.")
        return
    
    print(f"\n📋 Found {len(contacts)} contact(s):")
    print("-" * 70)
    for i, contact in enumerate(contacts, 1):
        print(f"{i:2d}. {contact}")
        if contact.notes:
            print(f"    📝 Notes: {contact.notes}")
        print(f"    📅 Added: {contact.created_at}")
        print("-" * 70)


def main():
    manager = ContactManager()
    
    print("🚀 Welcome to Contact Manager!")
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            manager.add_contact()
        
        elif choice == '2':
            print("\n👥 All Contacts")
            display_contacts(manager.get_all_contacts())
        
        elif choice == '3':
            print("\n🔍 Search Contacts")
            query = input("Enter search term: ").strip()
            if query:
                results = manager.search_contacts(query)
                display_contacts(results)
            else:
                print("❌ Please enter a search term")
        
        elif choice == '4':
            print("\n🗑️ Delete Contact")
            email = input("Enter email of contact to delete: ").strip()
            if email:
                contact = manager.find_contact_by_email(email)
                if contact:
                    print("\nContact to be deleted:")
                    display_contacts([contact])
                    confirm = input("Are you sure you want to delete this contact? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        success, message = manager.delete_contact(email)
                        print(f"{'✅' if success else '❌'} {message}")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("❌ Contact not found.")
            else:
                print("❌ Please enter an email.")
        
        elif choice == '5':
            contacts = manager.get_all_contacts()
            print("\n📊 Contact Statistics")
            print(f"Total contacts: {len(contacts)}")
            if contacts:
                domains = {}
                for contact in contacts:
                    domain = contact.email.split('@')[1].lower()
                    domains[domain] = domains.get(domain, 0) + 1
                
                print("Top email domains:")
                for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {domain}: {count}")
        
        elif choice == '6':
            print("👋 Goodbye! Your contacts have been saved.")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
