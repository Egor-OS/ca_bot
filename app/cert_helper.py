from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve_all
from asn1crypto import _types
from pyhanko.sign.validation import async_validate_pdf_signature
from pyhanko.pdf_utils.reader import PdfFileReader

class Cert_Helper:
    def decode(self, str_):
        return ' '.join('%02X' % c for c in _types.bytes_to_list(str_))

    def get_bytes_cert_pdf(self, file_name):
        with open(file_name, 'rb') as doc:
            pdf_file = PdfFileReader(doc)
            res = []
            for i in pdf_file.embedded_signatures:
                res.append(self.get_pub_key(self.decode(i.pkcs7_content)))
            return res

    def get_bytes_cert_fdf(self,file_name):
        with open(file_name, 'rb') as fdf_file:
            pars = PDFParser(fdf_file)
            doc = PDFDocument(pars)
            fields = resolve_all(doc.catalog['FDF'])['PPK']['Import'][0]['Certs'][0]
            return fields

    def get_pub_key(self, hex_str):
        pos = hex_str.find('06 09 2A 86 48 86 F7 0D 01 01 01')
        pos = hex_str[:pos].rfind('30 ')
        pos = hex_str[:pos].rfind('30 ')
        cert_str_hex = hex_str[pos:]
        cert_str_hex = cert_str_hex.split(' ')
        count_oct = 0
        if cert_str_hex[1] == '81':
            count_oct = 1
        elif cert_str_hex[1] == '82':
            count_oct = 2
        lenght_ = None
        add = None
        if count_oct == 1:
            lenght_ = cert_str_hex[2]
            add = 3
        elif count_oct == 2:
            lenght_ = cert_str_hex[2] + cert_str_hex[3]
            add = 4
        else:
            lenght_ = cert_str_hex[1]
            add = 2

        lenght_ = int(lenght_, 16)

        cert_str_hex = cert_str_hex[:lenght_ + add]
        cert_str_hex = " ".join(cert_str_hex)
        return cert_str_hex

    def get_pub_key_pdf(self,path):
        res = []
        bytes_pdf = self.get_bytes_cert_pdf(path)
        for i in bytes_pdf:
            res.append(str(i).replace(' ',''))
        return res

    def get_pub_key_fdf(self,path):
        try:
            bytes_pdf = self.get_bytes_cert_fdf(path)
            return self.get_pub_key(self.decode(bytes_pdf))
        except Exception:
            return False

    async def check_valid_cert(self,path):
        try:
            with open(path, 'rb') as doc:
                a = PdfFileReader(doc)
                for i in a.embedded_signatures:
                    res = await async_validate_pdf_signature(i)
                    if not res.valid:
                        return False
                return True
        except Exception:
            return False








