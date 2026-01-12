from flask import Blueprint
staffobj = Blueprint('bpstaff',__name__,template_folder='templates',static_folder='static',url_prefix='/staff')

from pkg.staff import routes