import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

DB_FILE = 'database.json'

class Database:
    def __init__(self):
        self.db_file = DB_FILE
        self.data = {
            'participants': {},  # Dicionário vazio
            'blacklist': [],
            'config': {
                'hashtag': None,
                'hashtag_locked': False,
                'bonus_roles': {},
                'tag_enabled': False,
                'server_tag': None,
                'tag_quantity': 1,
                'chat_lock_enabled': False,
                'chat_lock_channel': None,
                'inscricao_channel': None
            }
        }
        self.load()
    
    def load(self):
        try:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except Exception as e:
            print(f'Erro ao carregar database: {e}')
    
    def save(self):
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logging.info('Banco de dados salvo com sucesso')
        except Exception as e:
            logging.error(f'Erro ao salvar banco de dados: {str(e)}')
    
    def add_participant(self, user_id: str, first_name: str, last_name: str, 
                   full_name: str, message_id: str, tickets: dict, registered_at: str):
        self.data['participants'][user_id] = {
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
            'message_id': message_id,
            'tickets': tickets,
            'registered_at': registered_at
        }
        self.save()
    
    def remove_participant(self, user_id: str):
        if user_id in self.data['participants']:
            del self.data['participants'][user_id]
            self.save()
    
    def get_participant(self, user_id: str) -> Optional[Dict]:
        return self.data['participants'].get(user_id)
    
    def is_registered(self, user_id: str) -> bool:
        try:
            # Garante que user_id é string
            user_id = str(user_id)
            # Log mais detalhado
            logging.info(f'Verificando registro do usuário {user_id}')
            logging.info(f'Database atual: {self.data}')
            return user_id in self.data['participants']
        except Exception as e:
            logging.error(f'Erro ao verificar registro: {e}')
            return False
    
    def is_name_taken(self, first_name: str, last_name: str) -> bool:
        full_name = f"{first_name} {last_name}"
        return any(p['full_name'] == full_name for p in self.data['participants'])
    
    def get_all_participants(self) -> Dict:
        # Retorna o dicionário diretamente
        return self.data['participants']
    
    def update_tickets(self, user_id: str, tickets: Dict):
        participant = self.get_participant(user_id)
        if participant:
            participant['tickets'] = tickets
            self.save()
    
    def add_to_blacklist(self, user_id: str, username: str, reason: str):
        self.data['blacklist'].append({
            'user_id': user_id,
            'username': username,
            'reason': reason,
            'added_at': datetime.now().isoformat()
        })
        self.save()
    
    def remove_from_blacklist(self, user_id: str):
        self.data['blacklist'] = [u for u in self.data['blacklist'] if u['user_id'] != user_id]
        self.save()
    
    def is_blacklisted(self, user_id: str) -> bool:
        return any(u['user_id'] == user_id for u in self.data['blacklist'])
    
    def get_blacklist(self) -> List[Dict]:
        return self.data['blacklist']
    
    def set_hashtag(self, hashtag: str):
        self.data['config']['hashtag'] = hashtag
        self.save()
    
    def lock_hashtag(self):
        self.data['config']['hashtag_locked'] = True
        self.save()
    
    def add_bonus_role(self, role_id: str, role_name: str, quantity: int, abbreviation: str):
        self.data['config']['bonus_roles'][role_id] = {
            'name': role_name,
            'quantity': quantity,
            'abbreviation': abbreviation
        }
        self.save()
    
    def remove_bonus_role(self, role_id: str):
        if role_id in self.data['config']['bonus_roles']:
            del self.data['config']['bonus_roles'][role_id]
            self.save()
    
    def set_tag_enabled(self, enabled: bool, tag: Optional[str] = None, quantity: Optional[int] = None):
        self.data['config']['tag_enabled'] = enabled
        self.data['config']['server_tag'] = tag
        if quantity is not None:
            self.data['config']['tag_quantity'] = quantity
        self.save()
    
    def clear_participants(self):
        # Muda de lista para dicionário vazio
        self.data['participants'] = {}
        self.data['config']['hashtag_locked'] = False
        self.save()
    
    def set_chat_lock(self, enabled: bool, channel_id: Optional[str] = None):
        self.data['config']['chat_lock_enabled'] = enabled
        if channel_id is not None:
            self.data['config']['chat_lock_channel'] = channel_id
        self.save()
    
    def clear_all(self):
        self.data = {  # Reset completo
            'participants': {},  # Dicionário vazio
            'blacklist': [],
            'config': {
                'hashtag': None,
                'hashtag_locked': False,
                'bonus_roles': {},
                'tag_enabled': False,
                'server_tag': None,
                'tag_quantity': 1,
                'chat_lock_enabled': False,
                'chat_lock_channel': None,
                'inscricao_channel': None
            }
        }
        self.save()
    
    def get_statistics(self) -> Dict:
        total_tickets = 0
        tickets_by_role = {}
        tickets_by_tag = 0
        
        # Corrige iteração sobre dicionário
        for user_id, p in self.data['participants'].items():
            tickets = p['tickets']
            total_tickets += 1
            
            for role_name, role_data in tickets.get('roles', {}).items():
                total_tickets += role_data['quantity']
                tickets_by_role[role_name] = tickets_by_role.get(role_name, 0) + 1
            
            if tickets.get('tag'):
                total_tickets += tickets['tag']
                tickets_by_tag += 1
        
        return {
            'total_participants': len(self.data['participants']),
            'total_tickets': total_tickets,
            'tickets_by_role': tickets_by_role,
            'tickets_by_tag': tickets_by_tag
        }
    
    def set_inscricao_channel(self, channel_id: str):
        self.data['config']['inscricao_channel'] = str(channel_id)
        try:
            self.save()
        except Exception:
            pass

    def get_inscricao_channel(self) -> Optional[str]:
        return self.data['config'].get('inscricao_channel')

db = Database()
