import os


class Commands:
    class Checkers:
        @staticmethod
        def file(path: str, exists: bool):
            return (
                (lambda: os.path.isfile(path))
                if exists
                else (lambda: not os.path.isfile(path))
            )

        @staticmethod
        def folder(path: str, exists: bool):
            return (
                (lambda: os.path.isdir(path))
                if exists
                else (lambda: not os.path.isdir(path))
            )

        @staticmethod
        def folder_exists(path: str):
            return lambda: os.path.isdir(path)

        @staticmethod
        def folder_not_exists(path: str):
            return lambda: not os.path.isdir(path)

    # ---------------------------------------------- - - -
    # User
    @staticmethod
    def user(command: str):
        return f"sudo -u {os.getlogin()} {command}"

    # ---------------------------------------------- - - -
    # Environment
    @staticmethod
    def env_create(env_dir: str) -> str:
        return f"python -m venv {env_dir}"

    @staticmethod
    def env_dependencies(env_dir: str, requirements_filepath: str):
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r {requirements_filepath}"

    @staticmethod
    def env_freeze(env_dir: str, requirements_filepath: str):
        return f"source {env_dir}/bin/activate && pip freeze > {requirements_filepath}"

    @staticmethod
    def env_freeze_added(requirements_filepath: str, output_filepath: str):
        return f"diff -u /usr/share/vixen/vixen_requirements.txt {requirements_filepath} | grep '^+[^+]' | sed 's/^+//' > {output_filepath}"

    @staticmethod
    def env_install(env_dir: str, entry: str) -> str:
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir {entry}"

    @staticmethod
    def env_remove(env_dir: str, package_name: str) -> str:
        return f"source {env_dir}/bin/activate && pip install --no-cache-dir --upgrade pip && pip uninstall --no-cache-dir {package_name}"

    @staticmethod
    def env_path_executable(env_dir: str, file: str):
        return f'sed -i "1s|.*|#!{env_dir}/bin/python3|" {file}'

    @staticmethod
    def folder_remove_build(package_dir: str) -> str:
        return f"rm -r {package_dir}/build && rm -r {package_dir}/vx_libraries.egg-info"

    # ---------------------------------------------- - - -
    # Folders
    @staticmethod
    def folder_create(dir: str) -> str:
        return f"mkdir -p {dir}"

    @staticmethod
    def folder_remove(dir: str) -> str:
        return f"rm -r {dir}"

    @staticmethod
    def folder_copy(source: str, destination: str, force: bool = False):
        return f"cp -r{'f' if force else ''} {source} {destination}"

    # ---------------------------------------------- - - -
    # Files
    @staticmethod
    def file_copy(source: str, destination: str, force: bool = False):
        return f"cp {'-f' if force else ''} {source} {destination}"

    @staticmethod
    def file_remove(file: str):
        return f"rm {file}"

    # ---------------------------------------------- - - -
    # Files and folder
    @staticmethod
    def rename(source: str, destination: str):
        return f"mv {source} {destination}"

    # ---------------------------------------------- - - -
    # Git
    @staticmethod
    def git_get_archive(
        destination: str,
        repository: str,
        branch: str = "main",
        git_url: str = "https://github.com/vixen-shell",
    ):
        url = f"{git_url}/{repository}/archive/refs/heads/{branch}.zip"
        archive = "/tmp/vx-git-archive.zip"

        curl = f"curl -s -L {url} -o {archive}"
        unzip = f"unzip -o {archive} -d {destination}"
        rm_tmp = f"rm {archive}"

        return f"{curl} && {unzip} && {rm_tmp}"

    # ---------------------------------------------- - - -
    # Yarn
    @staticmethod
    def yarn_install(package_dir: str):
        return f"cd {package_dir} && yarn install"

    @staticmethod
    def yarn_build(package_dir: str):
        return f"cd {package_dir} && yarn build"

    # ---------------------------------------------- - - -
    # JSON
    @staticmethod
    def json_patch_feature_name_property(file: str, name: str):
        old_field = '"name": "feature"'
        new_field = f'"name": "{name}"'
        return f"sed -i 's/{old_field}/{new_field}/' {file}"
