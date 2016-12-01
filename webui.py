#!/usr/bin/env python
import ConfigParser
import os
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf.csrf import CsrfProtect
from flask import Flask, send_file, render_template
from werkzeug.utils import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired
from dotcarto import DotCartoFile


class Config(object):
    """
    Looks for config options in a config file or as an environment variable
    """
    def __init__(self, config_file_name):
        self.config_parser = ConfigParser.RawConfigParser()
        self.config_parser.read(config_file_name)

    def get(self, section, option):
        """
        Tries to find an option in a section inside the config file. If it's not found or if there is no
        config file at all, it'll try to get the value from an enviroment variable built from the section
        and options name, by joining the uppercase versions of the names with an underscore. So, if the section is
        "platform" and the option is "secret_key", the environment variable to look up will be PLATFORM_SECRET_KEY
        :param section: Section name
        :param option: Optionname
        :return: Configuration value
        """
        try:
            return self.config_parser.get(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return os.environ.get("%s_%s" % (section.upper(), option.upper()), None)


config = Config("dotcarto.conf")

app = Flask(__name__)
if config.get("webui", "debug"):
    app.debug = True
app.secret_key = config.get("webui", "secret_key")
CsrfProtect(app)


class DotCartoForm(FlaskForm):
    carto_api_endpoint = StringField("CARTO API endpoint", validators=[DataRequired()], description="For carto.com cloud accounts: https://YOUR_USER_NAME.carto.com/api/")
    carto_api_key = StringField("CARTO API key", validators=[DataRequired()], description='Found on the "Your API keys" section of your user profile')
    original_dotcarto_file = FileField("Original .carto file", validators=[FileRequired(), FileAllowed(["carto"], ".carto files only!")],
                                       description=".carto file where datasets will be swapped")
    old_dataset_names = StringField("Old dataset names", validators=[DataRequired()], description="Comma-separated list of old dataset names")
    new_dataset_names = StringField("New dataset names", validators=[DataRequired()], description="Comma-separated list of new dataset names, same order as above!!!")


@app.route("/", methods=["GET", "POST"])
def index():
    form = DotCartoForm()

    if form.validate_on_submit():
        filename = secure_filename(form.original_dotcarto_file.data.filename)

        dotcarto_file = DotCartoFile(form.original_dotcarto_file.data.stream, form.carto_api_endpoint.data, form.carto_api_key.data)

        new_dataset_names = form.new_dataset_names.data.split(",")
        for i, old_dataset_name in enumerate(form.old_dataset_names.data.split(",")):
            dotcarto_file.replace_dataset(old_dataset_name, new_dataset_names[i])

        return send_file(dotcarto_file.get_new(), attachment_filename=filename, as_attachment=True)

    return render_template("index.html", form=form)
