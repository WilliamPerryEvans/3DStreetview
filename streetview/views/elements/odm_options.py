from odk2odm import odm_requests
from wtforms import fields
from wtforms import validators
from wtforms import Form

def get_options_fields(options):
    """
    Converts dict with ODM task options to a dict with WTForms compatible fields
    :param options: dict with ODM options
    :return: dict with WTForms fields
    """
    opt_f = {}
    for opt in options:
        if opt["name"] in odm_requests.ODM_TASK_DEFAULT_OPTIONS:
            value = odm_requests.ODM_TASK_DEFAULT_OPTIONS[opt["name"]]
        else:
            value = opt["value"]
        kwargs = {
            "label": opt["name"],
            "default": value,
            "description": opt["help"]
        }
        # set specific options and choose field type
        if opt["type"] == "bool":
            field = fields.BooleanField
            kwargs["validators"] = [
                validators.DataRequired(),
            ]
        elif opt["type"] == "enum":
            field = fields.SelectField
            kwargs["choices"] = opt["domain"]
            kwargs["validators"] = [
                 validators.DataRequired(),
                 validators.AnyOf(opt["domain"])
             ]
        elif opt["type"] == "int":
            field = fields.IntegerField
            if opt["domain"] == "integer":
                kwargs["validators"]  = [
                    validators.DataRequired()
                ]
            elif opt["domain"] == "positive integer":
                kwargs["validators"] = [
                    validators.DataRequired(),
                    validators.NumberRange(min=0)
                ]
            else:
                raise ValueError(f"Found unexpected domain '{opt['domain']} in option {opt['name']}'")

        elif opt["type"] == "float":
            field = fields.FloatField
            if "positive" in opt["domain"] or "> 0" in opt["domain"]:
                kwargs["validators"] = [
                    validators.DataRequired(),
                    validators.NumberRange(min=0.),
                ]
            else:
                kwargs["validators"] = [
                    validators.DataRequired(),
                ]
        elif opt["type"] == "string":
            field = fields.StringField
            kwargs["validators"] = [validators.DataRequired()]
        else:
            print(f"Option {opt['name']} is not yet parsed")

        # now parse the option to WTForms field
        opt_f[opt["name"]] = field(**kwargs)
    return opt_f

class OdmOptionsForm(Form):
    """
    https://wtforms.readthedocs.io/en/2.3.x/specific_problems/
    Options form for ODM tasks. Different option types are:
    - bool: yes/no
    - enum: list of choices
    - float: float
    - int: int
    - string:
    "value" annotates the default value
    "
    """
    # for now only add a submit field. Rest will be parsed with a monkey-patch
    submit = fields.SubmitField('Submit')
