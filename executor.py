import subprocess
import sys
import os
import ast
import logging
from typing import Tuple, List
from package_manager import PackageManager

logger = logging.getLogger(__name__)

class PythonExecutor:
    def __init__(self, package_manager: PackageManager):
        self.package_manager = package_manager
        
    def extract_imports(self, file_path: str) -> List[str]:
        """Python dosyasındaki import'ları bul"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
                        
        except Exception as e:
            logger.error(f"Import analizi hatası: {e}")
            
        return list(set(imports))
    
    def install_requirements(self, file_path: str) -> Tuple[bool, str]:
        """Gerekli paketleri yükle"""
        imports = self.extract_imports(file_path)
        missing_packages = []
        
        for imp in imports:
            if imp not in ['os', 'sys', 're', 'json', 'datetime', 'math', 
                          'random', 'time', 'collections', 'itertools']:  # Built-in modüller
                if not self.package_manager.is_package_installed(imp):
                    missing_packages.append(imp)
                    
        if missing_packages:
            logger.info(f"📦 Eksik paketler: {missing_packages}")
            results = self.package_manager.install_packages(missing_packages)
            
            failed = [pkg for pkg, success in results.items() if not success]
            if failed:
                return False, f"Paketler yüklenemedi: {', '.join(failed)}"
                
        return True, "Tüm paketler yüklendi"
    
    def execute_file(self, file_path: str) -> Tuple[bool, str, str]:
        """Python dosyasını çalıştır"""
        try:
            # Önce gerekli paketleri yükle
            success, message = self.install_requirements(file_path)
            if not success:
                return False, "", message
                
            # Dosyayı çalıştır
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(file_path) or None
            )
            
            if result.returncode == 0:
                return True, result.stdout, result.stderr
            else:
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "", "Zaman aşımı (60 saniye)"
        except Exception as e:
            return False, "", str(e)
