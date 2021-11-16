from odk2odm import odm_requests
from wtforms import fields
from wtforms import validators
from wtforms import Form
from flask_wtf import FlaskForm
import json
import numpy as np

def get_options_fields(options, sort=False):
    """
    Converts dict with ODM task options to a dict with WTForms compatible fields
    :param options: dict with ODM options
    :return: dict with WTForms fields
    """
    if sort:
        # first sort
        index = list(np.argsort([opt[sort] for opt in options]))
    options = [options[i] for i in index]
    opt_f = {}
    for opt in options:
        if opt["name"] in odm_requests.ODM_TASK_DEFAULT_OPTIONS:
            value = odm_requests.ODM_TASK_DEFAULT_OPTIONS[opt["name"]]
        else:
            value = opt["value"]
        if len(opt["value"]) > 0:
            opt_validators = [
                # validators.InputRequired()
            ]
        else:
            opt_validators = []
        kwargs = {
            "label": opt["name"],
            "default": value,
            "description": opt["help"]
        }
        # set specific options and choose field type
        if opt["type"] == "bool":
            field = fields.BooleanField
            kwargs["validators"] = opt_validators
            if isinstance(value, str):
                kwargs["default"] = json.loads(value.lower())
            else:
                kwargs["default"] = value
        elif opt["type"] == "enum":
            field = fields.SelectField
            kwargs["choices"] = opt["domain"]
            kwargs["validators"] = opt_validators + [validators.AnyOf(opt["domain"])]
            kwargs["default"] = value
        elif opt["type"] == "int":
            field = fields.IntegerField
            if opt["domain"] == "integer":
                kwargs["validators"]  = opt_validators
            elif opt["domain"] == "positive integer":
                kwargs["validators"] = opt_validators + [validators.NumberRange(min=0)]
            else:
                raise ValueError(f"Found unexpected domain '{opt['domain']} in option {opt['name']}'")
            kwargs["default"] = int(value)
        elif opt["type"] == "float":
            field = fields.FloatField
            if "positive" in opt["domain"] or "> 0" in opt["domain"]:
                kwargs["validators"] = [validators.InputRequired(), validators.NumberRange(min=0.0)]
            else:
                kwargs["validators"] = opt_validators
            kwargs["default"] = float(value)
        elif opt["type"] == "string":
            field = fields.StringField
            kwargs["validators"] = opt_validators
        else:
            print(f"Option {opt['name']} is not yet parsed")

        # now parse the option to WTForms field
        opt_f[opt["name"]] = field(**kwargs)
    return opt_f

def parse_options(form):
    """
    Converts dict with key values to list of dicts with "name" and "value" key-value pairs, needed to post options in task
    If the dict contains a csrf-token then that will be left out
    :param options: dict with k, v pairs ODM options
    :return: list with dicts with "name" and "value"
    """
    return [{"name": f.label.text, "value": f.data} for f in form if (f.label.text != "CSRF Token" and f.data != f.default)]

class OdmOptionsForm(FlaskForm):
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
    # for now just pass. Rest will be parsed with a monkey-patch
    pass

class OdmTaskForm(FlaskForm):
    name = fields.StringField("name", validators=[validators.DataRequired()])

class OdmForm(FlaskForm):
    options_form = fields.FormField(OdmOptionsForm)
    task_form = fields.FormField(OdmTaskForm)