import re
from typing import Dict, List

def is_valid_name(name: str) -> bool:
    """Validar se o nome é real e não contém padrões inválidos"""
    if not name:
        return False

    # Remove espaços extras
    name = name.strip()

    # Verifica se tem pelo menos 2 caracteres
    if len(name) < 2:
        return False

    # Verifica se contém apenas letras e espaços (sem números ou símbolos)
    import re
    if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', name):
        return False

    # Verifica se começa com número (ex: 3rafael)
    if re.match(r'^\d', name):
        return False

    # Verifica se tem partes muito curtas (ex: "li souza" - "li" tem 2 letras)
    # Nomes com 1 ou 2 letras são suspeitos
    parts = name.split()
    for part in parts:
        if len(part) <= 2:
            return False

    # Verifica se tem caracteres repetidos demais (ex: "aaaa", "xxxx")
    if re.search(r'(.)\1{3,}', name.lower()):
        return False

    # Verifica se não é apenas consoantes ou vogais
    vowels = set('aeiouáéíóúâêîôûãõAEIOUÁÉÍÓÚÂÊÎÔÛÃÕ')
    has_vowel = any(c in vowels for c in name)
    has_consonant = any(c.isalpha() and c not in vowels for c in name)

    if not (has_vowel and has_consonant):
        return False

    return True

def calculate_tickets(member, bonus_roles, tag_enabled, server_tag, tag_quantity):
    tickets = {
        'base': 1,
        'roles': {},
        'tag': 0
    }

    for role in member.roles:
        role_id = str(role.id)
        if role_id in bonus_roles:
            role_data = bonus_roles[role_id]
            tickets['roles'][role_data['name']] = {
                'quantity': role_data['quantity'],
                'abbreviation': role_data['abbreviation']
            }

    if tag_enabled and server_tag:
        # Verifica tanto no nickname quanto no username global
        display_name = member.display_name or ''
        username = member.name or ''

        tag_lower = server_tag.lower().strip()
        if tag_lower in display_name.lower() or tag_lower in username.lower():
            tickets['tag'] = tag_quantity

    return tickets

def get_total_tickets(tickets: Dict) -> int:
    total = tickets.get('base', 1)

    for role_name, role_data in tickets.get('roles', {}).items():
        total += role_data['quantity']

    if tickets.get('tag'):
        total += tickets['tag']

    return total

def format_tickets_list(tickets: Dict) -> List[str]:
    ticket_list = ['1 ficha base']

    for role_name, role_data in tickets.get('roles', {}).items():
        ticket_list.append(f"+{role_data['quantity']} ficha(s) - {role_name} ({role_data['abbreviation']})")

    if tickets.get('tag'):
        ticket_list.append(f"+{tickets['tag']} ficha(s) - TAG do servidor")

    return ticket_list

def abbreviate_name(first_name: str, last_name: str) -> str:
    first_initial = last_name[0].upper() if last_name else ''
    second_initial = last_name[1].lower() if len(last_name) > 1 else ''
    return f"{first_name} {first_initial}{second_initial}."
