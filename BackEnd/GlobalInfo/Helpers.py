import sys
import linecache

import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage 
import BackEnd.GlobalInfo.Keys as connectKeys

from pymongo import MongoClient
import hashlib
import jwt

from datetime import datetime, date

import re
from unidecode import unidecode

# Connection for DB
def dbConnection():
    if connectKeys.dbconn == None:
        connectKeys.dbconn = MongoClient(connectKeys.strConnection).LinkThinks
    return connectKeys.dbconn

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    return

def passwordHash(strPassword):
    try:
        hashed = hashlib.sha256(bytes(strPassword, 'utf-8')).hexdigest()
        return hashed
    except Exception:
        PrintException()
        return ResponseMessage.message500

def deleteBlankAttributes(directory):

    try:

        newDirectory = {}

        for attribute in directory:
            if type(directory[attribute]) == str:
                directory[attribute] = directory[attribute].strip()
                
            if directory[attribute] != "":
                newDirectory = {
                    **newDirectory,
                    attribute: directory[attribute]
                }
        return newDirectory

    except Exception:
        PrintException()
        return ResponseMessage.message500
    
def DecodeTokenInfo(token):
    try:
        decoded = jwt.decode(token, connectKeys.tokenPassword, algorithms=['HS256'])
        
        return decoded

    except Exception:
        PrintException()
        return ""

def stringToDateYearFirst(strDate):
    try:
        date = datetime.strptime(strDate, '%Y-%m-%d')
        
        return date

    except Exception:
        PrintException()
        return ""

def createSearchRegex(strSearch):
    try:
        vocales = ['a', 'á', 'e', 'é', 'i', 'í', 'o', 'ó', 'u', 'ú']

        regexSearch = (re.escape(unidecode(strSearch))).lower()

        regex = ""

        for letter in regexSearch:
            temp = ""
            for v in range(0, len(vocales), 2):
                if letter == vocales[v]:
                    if letter == "i":
                        temp = "[iíy]"
                    else:
                        temp = "[" + vocales[v] + vocales[v+1] + "]"
            if temp != "":
                regex += temp
            elif letter == "b" or letter == "v":
                regex += "[bv]"
            elif letter == "c" or letter == "s" or letter == "z":
                regex += "[csz]"
            elif letter == "k" or letter == "q":
                regex += "[kq]u?"
            elif letter == "y":
                regex += "[iíy]"
            else:
                regex += letter
        
        return regex

    except Exception:
        PrintException()
        return ""

def stripObject(item):
    try:
        
        for i in item:
            if type(item[i]) == str:
                item[i] = item[i].strip()
        return item
    
    except Exception:
        PrintException()
        return item
#NEW
import os, base64, uuid, io
from PIL import Image  # <- usa Pillow
from . import Keys as K

def ensure_upload_dir():
    os.makedirs(K.UPLOAD_DIR, exist_ok=True)

def _ext_from_bytes(data: bytes) -> str:
    """
    Detecta el formato usando Pillow (imghdr fue removido en Python 3.13).
    """
    try:
        img = Image.open(io.BytesIO(data))
        fmt = (img.format or '').lower()
        mapping = {'jpeg': 'jpg', 'png': 'png', 'gif': 'gif', 'webp': 'webp'}
        return mapping.get(fmt, 'png')
    except Exception:
        # si no se pudo detectar, forzamos png
        return 'png'

def _is_allowed_ext(ext: str) -> bool:
    return ext.lower() in K.ALLOWED_EXTENSIONS

def save_image_bytes(data: bytes) -> str:
    """
    Guarda bytes de imagen en /static/uploads/products y regresa la URL pública.
    """
    ensure_upload_dir()
    if len(data) > K.MAX_IMAGE_SIZE:
        raise ValueError("Imagen demasiado grande (máximo 5MB).")

    ext = _ext_from_bytes(data)
    if not _is_allowed_ext(ext):
        raise ValueError("Tipo de imagen no permitido.")

    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(K.UPLOAD_DIR, filename)

    with open(dest, "wb") as f:
        f.write(data)

    # URL pública consumible por el front
    return f"{K.PUBLIC_BASE_URL}/{K.UPLOAD_SUBDIR}/{filename}".replace("\\", "/")

def save_image_from_base64(b64: str) -> str:
    """
    Acepta data URI (data:image/png;base64,...) o base64 crudo y devuelve strImageUrl.
    """
    if not b64:
        return ""
    # soporta data URI
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    data = base64.b64decode(b64)
    return save_image_bytes(data)
