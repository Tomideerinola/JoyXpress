from flask import Blueprint
userobj = Blueprint('bpuser',__name__,template_folder='templates',static_folder='static',url_prefix='/user')

# to make the local routes available

from pkg.user import routes #from. import routes 

