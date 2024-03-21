from flask import Blueprint, render_template, redirect, url_for, request
from fns import get_samples_status, listdir_no_hidden, is_unique_users, levels_game, get_login_users, get_version


app_pages = Blueprint('app_pages', __name__, template_folder='templates')


@app_pages.route('/login-info/<ter_name>', methods=['GET', 'POST'])
def get_login_user(ter_name):
    auth_user = get_login_users().get(ter_name.lower(), "empty")
    return auth_user


@app_pages.route('/gas_control', methods=['GET', 'POST'])
def gas_control():
    if not is_unique_users():
        return redirect(url_for("app_pages.double_auth_block", src_url=request.path))

    config = {
        "title": "Gas Control",
        "samples": get_samples_status()
    }
    print("open gas page")
    return render_template("TR1/p_gas_control.html", g_config=config)


@app_pages.route('/sample_release', methods=['GET', 'POST'])
def sample_release():
    config = {
        "title": "Experiment Status",
        "samples": get_samples_status()
    }
    print("open sample release page")
    return render_template("TR2/p_sample_release.html", g_config=config)


@app_pages.route('/gas_analysis', methods=['GET', 'POST'])
def gas_analysis():
    if not is_unique_users():
        return redirect(url_for("app_pages.double_auth_block", src_url=request.path))

    config = {
        "title": "Gas Analysis",
        "samples": get_samples_status()
    }
    print("open gas analysis page")
    return render_template("TR2/p_gas_analysis.html", g_config=config)


@app_pages.route('/elancell_upload', methods=['GET', 'POST'])
def elancell_upload():
    if not is_unique_users():
        return redirect(url_for("app_pages.double_auth_block", src_url=request.path))

    config = {
        "title": "Upload Results"
    }
    version_config = get_version("TR2").get("elancell")
    config.update(version_config)
    print("open Elancell page")
    return render_template("TR2/p_elancell_upload.html", g_config=config, samples=levels_game)


@app_pages.route('/elancell_breach', methods=['GET', 'POST'])
def elancell_breach():
    if not is_unique_users():
        return redirect(url_for("app_pages.double_auth_block", src_url=request.path))

    config = {
        "title": "IT Breach"
    }
    version_config = get_version("TR2").get("elancell")
    config.update(version_config)
    print("open Elancell breach page")
    return render_template("TR2/p_elancell_upload.html", g_config=config, samples=levels_game)


@app_pages.route('/cleanroom', methods=['GET', 'POST'])
def cleanroom():
    if not is_unique_users():
        return redirect(url_for("app_pages.double_auth_block", src_url=request.path))

    config = {
        "title": "Cleanroom Access"
    }
    version_config = get_version("TR2").get("cleanroom", {})
    config.update(version_config)

    print("open cleanroom access page")
    return render_template("TR2/p_cleanroom.html", g_config=config)


@app_pages.route('/media_control', methods=['GET', 'POST'])
def media_control():
    version_config = get_version("TR1").get("media", {})
    media_prefix = version_config.get("prefix", "")
    media_files = [video_file for video_file in listdir_no_hidden('static/media/') if
                   (video_file.startswith(media_prefix) and video_file.endswith(".webm"))]

    config = {
        "title": "Media Gallery",
        "files": sorted(media_files)
    }
 
    print("open media page")
    return render_template("TR1/p_media.html", g_config=config)

@app_pages.route('/media_control_rachel', methods=['GET', 'POST'])
def media_control_truth():
    version_config = get_version("TR3").get("media", {})
    media_prefix = version_config.get("prefix", "")
    media_files = [video_file for video_file in listdir_no_hidden('static/media/rachel') if
                   (video_file.endswith(".webm"))]

    config = {
        "title": "Rachel Tablet Gallery",
        "files": sorted(media_files)
    }
    print(media_files)
    print("open media page")
    return render_template("TR3/p_media.html", g_config=config, header_color = "red")


@app_pages.route('/personal_rachel', methods=['GET', 'POST'])
def personal_rachel():
    media_files = [video_file for video_file in listdir_no_hidden('static/media/rachel') if
                   video_file.endswith(".webm")]

    pdf_files = [file for file in listdir_no_hidden('static/pdfs') if file.endswith(".pdf")]

    config = {
        "title": "personal files",
        "files": sorted(media_files),
        "pdfs": pdf_files
    }
    print("open media page")
    return render_template("TR2/p_personal_rachel.html", g_config=config)

@app_pages.route('/personal_rachel_tablet', methods=['GET', 'POST'])
def personal_rachel_tablet():
   
    gallery_photos = ""
    pdf_folders = ""
    pdfs_dict = ""

    pdf_folders = sorted(
        [folder for folder in listdir_no_hidden('static/pdfs') if( not folder.endswith(".pdf") and not folder.endswith(".png"))])
    
    pdfs_dict = {folder: sorted([file for file in listdir_no_hidden(f'static/pdfs/{folder}') if file.endswith(".jpg")]) for folder in pdf_folders}

    gallery_photos = sorted(
            [img for img in listdir_no_hidden('static/imgs/gallery') if (img.endswith(".jpeg"))])

    pdf_files = [file for file in listdir_no_hidden('static/pdfs') if file.endswith(".pdf")]

    config = {
        "title": "personal files",
        "pdfs": sorted(pdf_files)
    }
    print("open media page")
    return render_template("TR3/p_personal_rachel.html", g_config=config, gallery_photos = gallery_photos, 
                           pdf_folders = pdf_folders, pdfs_dict = pdfs_dict, header_color = "red")


@app_pages.route('/double_auth', methods=['GET', 'POST'])
def double_auth_block():
    src_url = request.args.get('src_url', "/")
    print(f"src url is: {src_url}")
    config = {
        "title": "Incomplete Auth!"
    }
    if is_unique_users():
        return redirect(src_url)

    return render_template("noAuthFn.html", g_config=config, from_url=src_url)


@app_pages.errorhandler(404)
def page_not_found():
    return render_template('page_not_found.html'), 404


@app_pages.after_request
def adding_header_content(head):
    head.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    head.headers["Pragma"] = "no-cache"
    head.headers["Expires"] = "0"
    head.headers['Cache-Control'] = 'public, max-age=0'
    return head


if __name__ == "__main__":
    print("inside pages")
