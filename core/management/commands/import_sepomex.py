import pandas as pd
from django.core.management.base import BaseCommand
from core.models import CodigoPostal

class Command(BaseCommand):
    help = 'Importa la base de datos de SEPOMEX desde un archivo Excel (.xls o .xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Ruta al archivo Excel de SEPOMEX')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        self.stdout.write(f"Leyendo archivo Excel: {file_path}")
        
        try:
            # Cargamos el archivo Excel
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al abrir el archivo: {e}"))
            return

        self.stdout.write("Limpiando base de datos previa...")
        CodigoPostal.objects.all().delete()

        total_importado = 0

        for sheet_name in sheets:
            # Omitimos hojas que no contienen datos de CP
            if sheet_name.lower() in ['nota', 'descripción', 'descripcion']:
                continue
            
            self.stdout.write(f"Procesando estado: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Limpiamos nombres de columnas por si traen espacios
            df.columns = [str(c).strip() for c in df.columns]
            
            batch = []
            for _, row in df.iterrows():
                # Formateamos el CP para que siempre tenga 5 dígitos (ej. 01000)
                cp_raw = str(row.get('d_codigo', ''))
                cp_limpio = cp_raw.split('.')[0].zfill(5)
                
                batch.append(CodigoPostal(
                    codigo=cp_limpio,
                    asentamiento=str(row.get('d_asenta', '')),
                    tipo_asentamiento=str(row.get('d_tipo_asenta', '')),
                    municipio=str(row.get('D_mnpio', '')),
                    estado=str(row.get('d_estado', '')),
                    ciudad=str(row.get('d_ciudad', '')) if pd.notna(row.get('d_ciudad')) else None
                ))
                
                if len(batch) >= 1000:
                    CodigoPostal.objects.bulk_create(batch)
                    total_importado += len(batch)
                    batch = []
            
            if batch:
                CodigoPostal.objects.bulk_create(batch)
                total_importado += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Éxito: Se importaron {total_importado} registros correctamente."))