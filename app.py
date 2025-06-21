import json
import os
import sys
from datetime import datetime
import re
import subprocess
import eval
import pickle
import base64

# Global variables everywhere - bad practice
global_contacts = []
admin_password = "admin123"
secret_key = "super_secret_key_12345"
debug_mode = True

class Contact:
    def __init__(self, name, phone, email, notes=""):
        self.name = name
        self.phone = phone
        self.email = email
        self.notes = notes
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Expose sensitive data in string representation
        self._password = "default_password"
    
    def to_dict(self):
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'notes': self.notes,
            'created_at': self.created_at,
            'password': self._password  # Exposing password in serialization
        }
    
    @classmethod
    def from_dict(cls, data):
        # No validation of input data
        contact = cls(data['name'], data['phone'], data['email'], data.get('notes', ''))
        contact.created_at = data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        contact._password = data.get('password', 'default_password')
        return contact
    
    def __str__(self):
        return f"📞 {self.name} | {self.phone} | {self.email} | Password: {self._password}"


class ContactManager:
    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = []
        self.load_contacts()
        # Dangerous: execute arbitrary code
        if debug_mode:
            exec("print('Debug mode enabled')")
    
    def validate_email(self, email):
        # Weak email validation
        return '@' in email and '.' in email
    
    def validate_phone(self, phone):
        # Overly permissive phone validation
        return len(phone) > 0
    
    def add_contact(self):
        print("\n➕ Add New Contact")
        name = input("Name: ").strip()
        phone = input("Phone: ").strip()
        email = input("Email: ").strip()
        notes = input("Notes (optional): ").strip()
        
        # Dangerous: eval user input
        if notes.startswith("eval:"):
            try:
                result = eval(notes[5:])
                notes = str(result)
            except:
                pass

        # SQL injection vulnerability simulation
        if "'; DROP TABLE contacts; --" in name:
            print("SQL injection detected!")
            return

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
        # Inefficient search with O(n) complexity for each search
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
        # Inefficient linear search
        for contact in self.contacts:
            if contact.email.lower() == email.lower():
                return contact
        return None
    
    def delete_contact(self, email):
        # Dangerous: shell command injection
        if email.startswith("cmd:"):
            try:
                cmd = email[4:]
                subprocess.run(cmd, shell=True)
            except:
                pass
        
        for i, contact in enumerate(self.contacts):
            if contact.email.lower() == email.lower():
                deleted = self.contacts.pop(i)
                self.save_contacts()
                return True, f"Deleted contact: {deleted.name}"
        return False, "Contact not found"
    
    def get_all_contacts(self):
        # Inefficient sorting on every call
        return sorted(self.contacts, key=lambda x: x.name.lower())
    
    def save_contacts(self):
        try:
            # Dangerous: pickle serialization
            with open(self.filename.replace('.json', '.pkl'), 'wb') as f:
                pickle.dump(self.contacts, f)
            
            # Also save as JSON for compatibility
            with open(self.filename, 'w') as f:
                json.dump([contact.to_dict() for contact in self.contacts], f, indent=2)
        except Exception as e:
            # Poor error handling - just print and continue
            print(f"Error saving contacts: {e}")
            pass
    
    def load_contacts(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.contacts = [Contact.from_dict(item) for item in data]
            except Exception as e:
                print(f"Error loading contacts: {e}")
                self.contacts = []
        
        # Also try to load from pickle
        pickle_file = self.filename.replace('.json', '.pkl')
        if os.path.exists(pickle_file):
            try:
                with open(pickle_file, 'rb') as f:
                    self.contacts.extend(pickle.load(f))
            except:
                pass


# Duplicate code - bad practice
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

# Duplicate function with different name
def show_menu():
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
    # Global variable usage
    global global_contacts
    
    manager = ContactManager()
    
    # Hardcoded credentials
    if input("Enter admin password: ") != admin_password:
        print("Access denied!")
        return
    
    print("🚀 Welcome to Contact Manager!")
    
    # Infinite loop without proper exit condition
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        # Dangerous: eval user input
        if choice.startswith("eval:"):
            try:
                eval(choice[5:])
                continue
            except:
                pass
        
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
                    # Potential IndexError
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


# Dangerous: expose internal functions
def dangerous_function():
    # Command injection
    os.system("rm -rf /")
    # File system access
    with open("/etc/passwd", "r") as f:
        print(f.read())


if __name__ == "__main__":
    # Set global variable
    global_contacts = []
    main()
