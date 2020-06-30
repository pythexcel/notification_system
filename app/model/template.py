from app import mongo
from bson.objectid import ObjectId



def assign_letter_heads( letterhead_id ):
    letter_head_details = mongo.db.letter_heads.find_one({ "_id": ObjectId(letterhead_id) })
    if letter_head_details is not None:
        header = letter_head_details['header_value']
        footer = letter_head_details['footer_value']
        return { 'header': header, 'footer': footer }
    else:
        raise Exception("No letterhead available for this letterhead_id")

def attach_letter_head( header, footer, message):
    download_pdf = "#letter_head #content #letter_foot"
    if header is not None:
        download_pdf = download_pdf.replace("#letter_head", header)
    else:
        download_pdf = download_pdf.replace("#letter_head", '')
    download_pdf = download_pdf.replace("#content", message)
    if footer is not None:
        download_pdf = download_pdf.replace("#letter_foot", footer)
    else:
        download_pdf = download_pdf.replace("#letter_foot", '')
    return download_pdf









