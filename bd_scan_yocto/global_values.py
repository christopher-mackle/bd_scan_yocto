script_version = '1.0.11'
bdio = []
bdio_comps_layers = []
bdio_comps_recipes = []
packages_list = []
recipes_dict = {}
recipe_layer_dict = {}
layers_list = []
bdio_proj_rel_list = []
# replace_recipes_dict = {}

logfile = ''
bd_trustcert = False
bd_api = ''
bd_url = ''
bd_project = ''
bd_version = ''
# offline = False
oe_build_env = ''
oe_build_envpath = '.'
deploy_dir = ''
download_dir = ''
pkg_dir = ''
image_pkgtype = ''
manifest_file = ''
machine = ''
cve_check = True
cve_check_file = ''
detect_jar = ''
target = ''
testmode = False
debug = False
skip_detect_for_bitbake = False
bd = None
# report_file = ''
extended_scan_layers = []
exclude_layers = []
detect_opts = ''
snippets = False
ignore_components = True
binary_scan = False
binary_scan_exts = "*.rpm,*.deb,*.tar,*.gz,*.ipk,*.zip,*.xz"
detect_fix = False
