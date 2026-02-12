import subprocess
import sys
import pkg_resources
import logging
import re
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PackageManager:
    def __init__(self):
        self.pip_path = sys.executable.replace('python', 'pip')
        
    def get_installed_packages(self) -> List[str]:
        """Yüklü paketleri listele"""
        try:
            packages = [f"{dist.project_name}=={dist.version}" 
                       for dist in pkg_resources.working_set]
            return sorted(packages)
        except Exception as e:
            logger.error(f"Paket listesi alınamadı: {e}")
            return []
    
    def install_packages(self, packages: List[str]) -> Dict[str, bool]:
        """Paketleri yükle"""
        results = {}
        
        for package in packages:
            try:
                # Önce paket yüklü mü kontrol et
                if self.is_package_installed(package):
                    logger.info(f"{package} zaten yüklü")
                    results[package] = True
                    continue
                
                # Paketi yükle
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                success = result.returncode == 0
                results[package] = success
                
                if success:
                    logger.info(f"✅ {package} yüklendi")
                else:
                    logger.error(f"❌ {package} yüklenemedi: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.error(f"{package} yüklenirken zaman aşımı")
                results[package] = False
            except Exception as e:
                logger.error(f"{package} yüklenirken hata: {e}")
                results[package] = False
                
        return results
    
    def uninstall_package(self, package: str) -> bool:
        """Paket kaldır"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            if success:
                logger.info(f"✅ {package} kaldırıldı")
            else:
                logger.error(f"❌ {package} kaldırılamadı: {result.stderr}")
                
            return success
            
        except Exception as e:
            logger.error(f"Paket kaldırma hatası: {e}")
            return False
    
    def update_package(self, package: str) -> bool:
        """Paket güncelle"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", package],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            if success:
                logger.info(f"✅ {package} güncellendi")
            else:
                logger.error(f"❌ {package} güncellenemedi: {result.stderr}")
                
            return success
            
        except Exception as e:
            logger.error(f"Paket güncelleme hatası: {e}")
            return False
    
    def is_package_installed(self, package_name: str) -> bool:
        """Paket yüklü mü kontrol et"""
        try:
            # Paket adını temizle (versiyon vs varsa)
            package_name = re.sub(r'[=<>].*$', '', package_name)
            package_name = package_name.strip()
            
            # Paket yüklü mü kontrol et
            dist = pkg_resources.get_distribution(package_name)
            return True
        except pkg_resources.DistributionNotFound:
            return False
        except Exception:
            return False
    
    def check_missing_packages(self) -> List[str]:
        """Eksik veya güncel olmayan paketleri kontrol et"""
        missing_packages = []
        
        try:
            # requirements.txt varsa kontrol et
            try:
                with open('requirements.txt', 'r') as f:
                    requirements = f.read().splitlines()
                    
                for req in requirements:
                    if req and not req.startswith('#'):
                        if not self.is_package_installed(req):
                            missing_packages.append(req)
            except FileNotFoundError:
                logger.info("requirements.txt bulunamadı")
                
            # pip ile güncel olmayan paketleri kontrol et
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                for line in lines[2:]:  # İlk 2 satır başlık
                    if line.strip():
                        package = line.split()[0]
                        missing_packages.append(package)
                        
        except Exception as e:
            logger.error(f"Paket kontrol hatası: {e}")
            
        return list(set(missing_packages))  # Benzersiz yap
