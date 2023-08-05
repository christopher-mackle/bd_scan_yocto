# Synopsys Scan Yocto Script - bd_scan_yocto.py - v1.0

# PROVISION OF THIS SCRIPT
This script is provided under an OSS license as an example of how to use the Black Duck APIs to import components from a Yocto project manifest.

It does not represent any extension of licensed functionality of Synopsys software itself and is provided as-is, without warranty or liability.

If you have comments or issues, please raise a GitHub issue here. Synopsys support is not able to respond to support tickets for this OSS utility.

# INTRODUCTION
### OVERVIEW OF BD_SCAN_YOCTO

This `bd_scan_yocto.py` script is a utility intended to scan Yocto projects into Synopsys Black Duck. It examines the Yocto project and environment and uses Synopsys Detect to perform multiple scans, with additional actions to optimise the scan result to produce a more comprehensive scan than previous methods.

Synopsys Detect is the default scan utility for Black Duck and includes support for Yocto projects, however Synopsys Detect Yocto scans will only identify standard recipes obtained from Openembedded.org, and will not cover modified or custom recipes, recipes moved to new layers or where package versions or revisions have been changed.

This script combines the Synopsys Detect default Yocto scan with Black Duck Signature scanning of downloaded packages to create a more complete list of original, modified OSS and OSS embedded within custom packages. It also optionally supports snippet scanning of recipes in specific layers.

`Bd_scan_yocto` can also optionally identify the list of locally patched CVEs within a Yocto build which can then be marked as patched in the Black Duck project.

### SCANNING YOCTO IN BLACK DUCK USING SYNOPSYS DETECT

As described above, the standard, supported method of scanning a Yocto project is provided by Synopsys Detect (see [Synopsys Detect - scanning Yocto](https://sig-product-docs.synopsys.com/bundle/integrations-detect/page/packagemgrs/bitbake.html)).

To perform a standard Yocto scan using Synopsys Detect:
- Change to the poky folder of a Yocto project
- Run Synopsys Detect adding the options `--detect.tools=DETECTOR --detect.bitbake.package.names=core-image-sato`  (where `core-image-sato` is the package name).
- Synopsys Detect will look for the default OE initialization script (`oe-init-build-env`); you can use the option `--detect.bitbake.build.env=oe-init-script` if you need to specify an alternate init script (`oe-init-script` in this example).
- Detect can optionally inspect the build manifest to remove build dependencies if the option `--detect.bitbake.dependency.types.excluded=BUILD` is used (see [here](https://community.synopsys.com/s/document-item?bundleId=integrations-detect&topicId=properties%2Fdetectors%2Fbitbake.html] ) for more information).

However, Synopsys Detect can only identify unmodified, original recipes from [layers.openembedded.org](http://layers.openembedded.org/), meaning that many Yocto recipes which have been modified or other custom recipes will not be identified. This `bd_scan_yocto` script is intended to provide an enhanced, multi-factor scan for Yocto projects to attempt to provide a more comprehensive BOM including modified OSS packages and OSS within custom recipes. 

Note that Black Duck Signature scanning should not be used for an entire Yocto project because it contains a large number of project and configuration files, including the development packages needed to build the image. Furthermore, OSS package code can be modified locally by change/diff files meaning Signature scans of entire Yocto projects will consume large volumes of server resources and produce a Bill of Materials with a large number of additional components which are not deployed in the Yocto image.

### WHY BD_SCAN_YOCTO?

This script provides a multi-factor scan for Yocto projects combining the default Synopsys Detect Bitbake scan with other techniques to produce a more complete Bill of Materials including modified OSS packages and OSS within custom recipes.

It should be considered in the following scenarios:
- Where many standard OpenEmbedded recipes have been moved to new layers (meaning they will not be matched by Synopsys Detect)
- Where OpenEmbedded recipe versions or revisions have been modified from the original
- Where the project contains modified OSS recipes or custom recipes
- Where snippet scanning is required for recipes in specific layers
- Where locally patched CVEs need to be applied to the Black Duck project

The script operates on a built Yocto project, by identifying the build (license) manifest containing __only the recipes which are within the built image__ as opposed to the superset of all recipes used to build the distribution (including build tools etc.). The script also Signature scans the downloaded origin packages (before they are modified by local patching) to identify modified or custom recipes, with the option to expand archived sources and run Snippet scans for recipes in specified layers.

This script also optionally supports extracting a list of locally patched CVEs from Bitbake via the `cve_check` class and marking them as patched in the Black Duck project.

The script must be executed on a Linux workstation where Yocto has been installed and after a successful Bitbake build.

The script requires access to a Black Duck server via the API (see Prerequisites below).

### COMPARING BD_SCAN_YOCTO AGAINST IMPORT_YOCTO_BM

A previous script [import_yocto_bm](https://github.com/blackducksoftware/import_yocto_bm) was available to address some limitations of Synopsys Detect for Yocto, however it requires regular updates of the list of known OpenEmbedded recipes from the Black Duck KB which is difficult to maintain, and leads to inaccurate scanning when not updated.

Furthermore, `import_yocto_bm` did not support scanning non-OpenEmbedded recipes or custom recipes, including the option for snippet scanning of recipes in specific layers meaning that the resulting Bills of Materials were only partial.

# RUNNING BD_SCAN_YOCTO 
### SUPPORTED YOCTO PROJECTS

This script is designed to support Yocto versions 2.0 up to 4.2.

### PREREQUISITES

1. Must be run on Linux

1. Python 3 must be installed.

1. A supported Yocto environment is required.

1. The Yocto project must have been pre-built with a `license.manifest` file generated by the build. Downloaded package archives should be retained in the download folder and rpm packages in the rpm cache folder.

1. Black Duck server credentials (URL and API token) are required.

1. OPTIONAL: For patched CVE remediation in the Black Duck project, you will need to add the `cve_check` bbclass to the Yocto build configuration to generate the CVE check log output. Add the following line to the `build/conf/local.conf` file:

       INHERIT += "cve-check"

   The Yocto build command (e.g. `bitbake core-image-sato`)  will run the CVE check action to generate the required CVE log files without a full rebuild.

### INSTALLATION

Install the utility using pip - for example:

    pip3 install import_yocto_bm

Alternatively, clone the repository and run directly using:

    python3 import_yocto_bm/main.py

### USAGE

Change to the poky folder where the OE initialization script exists (`oe-init-build-env` by default).

The minimum data required to run the script is:

- Black Duck server URL
- Black Duck API token with scan permissions
- Black Duck project and project version name to be created
- OE initialization script (if not `oe-init-build-env`)
- Yocto target name (default `core-image-sato`)
- Yocto machine name (default `qemux86-64`)
- Full path to the `license.manifest` file for the specific build of interest

Run the command `bd_scan_yocto` without arguments to invoke the wizard to guide you through the required information and options.

The default behaviour of bd_scan_yocto is:
1. Locate the OE initialization script (default `oe-init-build-env`)
2. Extract information from the Bitbake environment (by running `bitbake -e`)
3. Run Synopsys Detect in Bitbake dependency scan mode to extract the standard OE recipes/dependencies (skip this step using the `--skip_detect_for_bitbake` option) to create the specified Black Duck project & version
4. Locate the software components and rpm packages downloaded during the build, and copy those matching the recipes from license.manifest to a temporary folder (if the option `--exclude_layers` is used then skip recipes within the specified layers)
5. If the option `--extended_scan_layers` is added with a list of layers, then expand the archives used by the recipes in the specified layers. These expanded archives will be snippet scanned
6. Run a signature scan using Synopsys Detect on the copied & expanded archives and rpm packages into the specified Black Duck project
7. Wait for scan completion, and then post-process the project version BOM to remove any identified sub-components from the unexpanded archives and rpm packages.

### COMMAND LINE OPTIONS
The `bd_scan_yocto` parameters for command line usage are shown below:

     -h, --help            show this help message and exit
     --blackduck_url BLACKDUCK_URL
                           Black Duck server URL (REQUIRED)
    --blackduck_api_token BLACKDUCK_API_TOKEN
                           Black Duck API token (REQUIRED)
     --blackduck_trust_cert
                           Black Duck trust server cert
     --detect-jar-path DETECT_JAR_PATH
                           Synopsys Detect jar path
     -p PROJECT, --project PROJECT
                           Black Duck project to create (REQUIRED)
     -v VERSION, --version VERSION
                           Black Duck project version to create (REQUIRED)
     --oe_build_env OE_BUILD_ENV
                           Yocto build environment config file (default 'oe-init-
                           build-env')
     -t TARGET, --target TARGET
                           Yocto target (default core-image-sato)
     -m MANIFEST, --manifest MANIFEST
                           Built license.manifest file)
     --machine MACHINE     Machine Architecture (for example 'qemux86-64')
     --skip_detect_for_bitbake
                           Skip running Detect for Bitbake dependencies
     --cve_check_only      Only check for patched CVEs from cve_check and update skipping scans
                           existing project
     --no_cve_check        Skip check for and update of patched CVEs
     --cve_check_file CVE_CHECK_FILE
                           CVE check output file (if not specified will be
                           determined from conf files)
     --wizard              Start command line wizard (Wizard will run by default
                           if config incomplete)
     --nowizard            Do not use wizard (command line batch only)
     --extended_scan_layers EXTENDED_SCAN_LAYERS
                           Specify a command-delimited list of layers where
                           packages within recipes will be expandedand Snippet
                           scanned
     --exclude_layers EXCLUDE_LAYERS
                           Specify a command-delimited list of layers where
                           packages within recipes will not be Signature scanned
     --download_dir DOWNLOAD_DIR
                           Download directory where original packages are
                           downloaded (usually poky/build/downloads)
     --rpm_dir RPM_DIR     Download directory where rpm packages are downloaded
                           (usually poky/build/tmp/deploy/rpm/<ARCH>)
     --debug               DEBUG mode - skip various checks


The script will use the invocation folder as the Yocto project folder (e.g. yocto_zeus/poky) by default.

The `--project` and `--version` options are required to define the Black Duck project and version names.

The Yocto target and machine values are required to locate the manifest and cve\_check log files and will be extracted from the Bitbake environment automatically, but the `--target` and `--machine` options can be used to specify these manually.

The most recent Bitbake output manifest file (located in the `build/tmp/deploy/licenses/<image>-<target>-<datetime>/license.manifest` file) will be located automatically. Use the `--manifest` option to specify the manifest file manually.

The most recent cve\_check log file `build/tmp/deploy/images/<arch>/<image>-<target>-<datetime>.rootfs.cve` will be located automatically if it exists. Use the `--cve_check_file` option to specify the cve\_check log file location manually (for example to use an older copy).

Use the `--cve_check_only` option to skip the scanning and creation of a project, only looking for a CVE check output log file to identify and patch matched CVEs within an existing Black Duck project (which must have been created previously).

Use the `--no_cve_check` option to skip the patched CVE identification and update of CVE status in the Black Duck project. 

### BLACK DUCK CONFIGURATION

You will need to specify the Black Duck server URL, API_TOKEN, project and version using command line options:

      --blackduck_url https://SERVER_URL
      --blackduck_api_token TOKEN
      --blackduck_trust_cert (specify if untrusted CA certificate used for BD server)
      --project PROJECT_NAME
      --version VERSION_NAME

You can also set the URL and API Token by setting environment variables:

      BLACKDUCK_URL=https://SERVER_URL
      BLACKDUCK_API_TOKEN=TOKEN

Where `SERVER_URL` is the Black Duck server URL and `TOKEN` is the Black Duck API token.

### EXAMPLE USAGE

To run the utility in wizard mode, simply use the command `import_yocto_bm` and it will ask questions to determine the scan parameters.

Use the option `--nowizard` to run in batch mode and bypass the wizard mode, noting that you will need to specify all required options on the command line correctly.

Use the following command to scan a Yocto build, create Black Duck project `myproject` and version `v1.0`, then update CVE patch status for identified CVEs (will require the OE environment to have been loaded previously):

    import_yocto_bm --blackduck_url https://SERVER_URL \
      --blackduck_api_token TOKEN \
      --blackduck_trust_cert \
      -p myproject -v v1.0

To scan a Yocto project specifying a different build manifest as opposed to the most recent one:

    import_yocto_bm --blackduck_url https://SERVER_URL \
      --blackduck_api_token TOKEN \
      --blackduck_trust_cert \
      -p myproject -v v1.0 \
      -m tmp/deploy/licenses/core-image-sato-qemux86-64-20200728105751/package.manifest

To skip the Synopsys Detect Yocto scan, Signature scan the downloaded package archives only:

    import_yocto_bm --blackduck_url https://SERVER_URL \
      --blackduck_api_token TOKEN \
      --blackduck_trust_cert \
      -p myproject -v v1.0 --skip_detect_for_bitbake

To perform a CVE check patch analysis ONLY (to update an existing Black Duck project created previously by the script with patched vulnerabilities) use the command:

    import_yocto_bm --blackduck_url https://SERVER_URL \
      --blackduck_api_token TOKEN \
      --blackduck_trust_cert \
      -p myproject -v v1.0 --cve_check_only

### CVE PATCHING

The Yocto `cve_check` class works on the Bitbake dependencies within the dev environment, and produces a list of CVEs identified from the NVD for ALL packages in the development environment.

This script can extract the packages from the build manifest (which will be a subset of those in the full Bitbake dependencies for build environment) and creates a Black Duck project.

The list of CVEs reported by `cve_check` will therefore be considerably larger than seen in the Black Duck project (which is the expected situation).

See the Prerequisites section above for details on how to configure this script to use the `cve_check` data.

# ADVANCED TOPICS

For a custom C/C++ recipe, or where other languages and package managers are used to build custom recipes, other types of scan could be considered in addition to the techniques used in this script.

For C/C++ recipes, the advanced [blackduck_c_cpp](https://pypi.org/project/blackduck-c-cpp/) utility could be used as part of the build to identify the compiled sources, system includes and operating system dependencies. You would need to modify the build command for the recipe to call the `blackduck-c-cpp` utility as part of a scanning cycle after it had been configured to connect to the Black Duck server.

For recipes where a package manager is used, then a standard Synopsys Detect scan in DETECTOR mode could be utilised to analyse the project dependencies.

Multiple scans can be combined into the same Black Duck project (ensure to use the Synopsys Detect option `--detect.project.codelocation.unmap=false` to stop previous scans from being unmapped).

# OUTSTANDING ISSUES

The identification of the Linux Kernel version from the Bitbake recipes and association with the upstream component in the KB has not been completed yet. Until an automatic identification is possible, the required Linux Kernel component can be added manually to the Black Duck project.

# FAQs

1. Can this utility be used on a Yocto image without access to the build environment?

   _No - this utility needs access to the Yocto build environment including the cache of downloaded components and rpm packages to perform scans._

# UPDATE HISTORY

## V1.0
- Initial version
