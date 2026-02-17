import yaml
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PortMapping:
    host: str
    container: str
    protocol: str = "tcp"

@dataclass
class ContainerInfo:
    name: str
    image: str
    ports: List[PortMapping]
    container_type: str
    is_web: bool
    warnings: List[str]

class DockerComposeParser:
    """
    Parser para archivos docker-compose.yml mejorado con detección de tipos.
    """

    def __init__(self, compose_content: str):
        self.content = compose_content
        self.parsed_data = None
        self.errors = []
        self.warnings = []

    def parse(self) -> Dict:
        try:
            self.parsed_data = yaml.safe_load(self.content)
        except yaml.YAMLError as e:
            return {
                'success': False,
                'error': 'Error de sintaxis YAML',
                'line': e.problem_mark.line if hasattr(e, 'problem_mark') else None,
                'column': e.problem_mark.column if hasattr(e, 'problem_mark') else None,
                'message': str(e.problem)
            }

        if not self._validate_structure():
            return {
                'success': False,
                'error': 'Estructura inválida',
                'message': 'El archivo no tiene la estructura esperada de docker-compose',
                'errors': self.errors
            }

        containers = self._extract_containers()

        return {
            'success': True,
            'containers': [self._container_to_dict(c) for c in containers],
            'warnings': self.warnings,
            'errors': self.errors
        }

    def _validate_structure(self) -> bool:
        if not isinstance(self.parsed_data, dict):
            self.errors.append("El archivo debe ser un diccionario YAML válido")
            return False
        if 'services' not in self.parsed_data:
            self.errors.append("Falta la sección 'services'")
            return False
        return True

    def _extract_containers(self) -> List[ContainerInfo]:
        containers = []
        for service_name, service_config in self.parsed_data['services'].items():
            ports = self._extract_ports(service_config)
            
            # Inteligencia de detección
            container_type = self._detect_type(service_name, service_config)
            is_web = self._detect_is_web(service_name, service_config, ports)

            container = ContainerInfo(
                name=service_name,
                image=service_config.get('image', 'No especificada'),
                ports=ports,
                container_type=container_type,
                is_web=is_web,
                warnings=[]
            )

            if not container.ports:
                container.warnings.append("No se declararon puertos.")

            containers.append(container)
        return containers

    def _detect_type(self, name, config) -> str:
        name_lower = name.lower()
        image = config.get('image', '').lower()
        
        detected = 'misc'
        # 1. Bases de Datos (Prioridad alta)
        if any(x in name_lower or x in image for x in ['postgres', 'mysql', 'mariadb', 'db', 'sql', 'mongo', 'postgis']):
            detected = 'database'
        # 2. Redis/Cache (Tratados como misc/general en este sistema)
        elif any(x in name_lower or x in image for x in ['redis', 'cache', 'memcached']):
            detected = 'misc'
        # 3. Web / Gateway / Frontend
        elif any(x in name_lower or x in image for x in ['gateway', 'nginx', 'web', 'frontend', 'proxy', 'app', 'front', 'httpd', 'apache', 'traefik']):
            detected = 'web'
        # 4. API / Backend
        elif any(x in name_lower or x in image for x in ['api', 'backend', 'server', 'flask', 'django', 'node', 'back', 'gunicorn', 'uvicorn']):
            detected = 'api'
        else:
            detected = 'misc'
            
        return detected

    def _detect_is_web(self, name, config, ports) -> bool:
        # Si tiene puertos y el nombre suena a gateway/web/api, es web
        name_lower = name.lower()
        if not ports:
            return False
        
        # Filtro de puertos típicos que NO son web
        for p in ports:
            c_port = int(str(p.container))
            if c_port in [5432, 3306, 6379, 27017]:
                return False
                
        if any(x in name_lower for x in ['web', 'gateway', 'nginx', 'frontend', 'api', 'backend', 'app']):
            return True
            
        return False

    def _extract_ports(self, service_config: Dict) -> List[PortMapping]:
        """
        Extrae y normaliza los puertos de la configuración del servicio.
        Soporta:
        - "80" (solo contenedor) -> host="auto"
        - "8080:80" (host:contenedor)
        - "127.0.0.1:8080:80" (ip:host:contenedor)
        - 80 (entero)
        - long syntax (dict)
        """
        extracted = []
        raw_ports = service_config.get('ports', [])
        
        if not raw_ports:
            return extracted

        for entry in raw_ports:
            host_port = "auto"
            container_port = None
            
            try:
                # Caso diccionario (long syntax)
                if isinstance(entry, dict):
                    container_port = str(entry.get('target', ''))
                    if 'published' in entry:
                        host_port = str(entry.get('published'))
                    
                # Caso string o entero (short syntax)
                else:
                    entry_str = str(entry).strip()
                    # Quitar protocolo ej: "80/tcp"
                    if '/' in entry_str:
                        entry_str = entry_str.split('/')[0]
                    
                    parts = entry_str.split(':')
                    
                    if len(parts) == 1:
                        # "80" -> Solo puerto contenedor
                        container_port = parts[0]
                    elif len(parts) == 2:
                        # "8080:80" -> host:container
                        host_port = parts[0]
                        container_port = parts[1]
                    elif len(parts) >= 3:
                        # "127.0.0.1:8080:80" -> ip:host:container
                        # Tomamos los dos últimos segmentos
                        host_port = parts[-2]
                        container_port = parts[-1]
                
                if container_port:
                    extracted.append(PortMapping(host=host_port, container=container_port))
            except Exception:
                continue
                
        return extracted

    def _container_to_dict(self, container: ContainerInfo) -> Dict:
        return {
            'name': container.name,
            'image': container.image,
            'ports': [{'host': p.host, 'container': p.container} for p in container.ports],
            'container_type': container.container_type,
            'is_web': container.is_web,
            'warnings': container.warnings
        }
