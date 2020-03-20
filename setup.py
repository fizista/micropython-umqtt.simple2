import os
import sys
import shutil
from pathlib import Path
from filecmp import dircmp
from glob import glob
from os.path import basename, splitext, join, dirname

__dir__ = Path(__file__).absolute().parent
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
import setuptools

sys.path.append("..")
import sdist_upip


def read(file_relative):
    file = __dir__ / file_relative
    with open(str(file)) as f:
        return f.read()


MINIFIED_DIR = Path('build_app')


class PythonMinifier(setuptools.Command):
    """A custom command to run Python Minifier"""

    description = 'run Python Minifier on Python source files'
    user_options = [
        ('minified-dir=', 'm', 'Path where the result is to be saved.'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.minified_dir = str(MINIFIED_DIR)

    def finalize_options(self):
        """Post-process options."""
        if self.minified_dir == str(MINIFIED_DIR):
            if not os.path.exists(str(MINIFIED_DIR)):
                os.mkdir(str(MINIFIED_DIR))

        if not os.path.isdir(self.minified_dir):
            raise Exception("Directory does not exist: {0}".format(self.minified_dir))

        if os.path.exists(str(Path(self.minified_dir) / 'umqtt')):
            shutil.rmtree(str(Path(self.minified_dir) / 'umqtt'))
        os.makedirs(str(Path(self.minified_dir) / 'umqtt'), exist_ok=True)
        print('OUT directory: ', self.minified_dir)

    def run(self):
        """Run command."""

        import python_minifier

        for file in os.listdir(str(__dir__ / 'src' / 'umqtt')):
            with open(str(__dir__ / 'src' / 'umqtt' / file)) as f:
                print('Minify: %s' % file)
                source = f.read()
                filename = file.split('/')[-1]
                out = python_minifier.minify(
                    source,
                    filename,
                    remove_annotations=True,
                    remove_pass=True,
                    remove_literal_statements=True,
                    combine_imports=False,
                    hoist_literals=False,
                    rename_locals=True,
                    preserve_locals=None,
                    rename_globals=False,
                    preserve_globals=None,
                    remove_object_base=False,
                    convert_posargs_to_args=False
                )
                with open(str(Path(self.minified_dir) / 'umqtt' / file), 'w') as f:
                    f.write(out)


from distutils import dir_util, dep_util, file_util, archive_util
from distutils import log


class SDistCommand(sdist_upip.sdist):
    """Custom build command."""

    def make_release_tree(self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        """
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        files_tree_fix = [f.replace(str(MINIFIED_DIR) + '/', '') for f in files]
        dir_util.create_tree(base_dir, files_tree_fix, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        if hasattr(os, 'link'):  # can make hard links on this system
            link = 'hard'
            msg = "making hard links in %s..." % base_dir
        else:  # nope, have to copy
            link = None
            msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file):
                log.warn("'%s' not a regular file -- skipping" % file)
            else:
                file_fix = file.replace(str(MINIFIED_DIR) + '/', '')
                dest = os.path.join(base_dir, file_fix)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)

    def run(self):
        self.run_command('minify')

        def print_diff_files(dcmp):
            is_diff = False
            for name in dcmp.diff_files:
                print("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))
                is_diff = True
            for sub_dcmp in dcmp.subdirs.values():
                is_diff = is_diff or print_diff_files(sub_dcmp)
            return is_diff

        dcmp = dircmp(str(MINIFIED_DIR), 'src_minimized')
        if print_diff_files(dcmp):
            raise Exception('There are differences in minimized files. '
                            'Compare %s and %s directories. They must be identical.' %
                            (str(MINIFIED_DIR), 'src_minimized'))

        super(SDistCommand, self).run()


setuptools.setup(
    name='micropython-umqtt.simple2',
    version='2.0.4',
    description='MQTT client for MicroPython.',
    long_description=read('README.rst'),
    long_description_content_type="text/x-rst",
    url='https://github.com/fizista/micropython-umqtt.simple2',
    author='Wojciech Banaś',
    author_email='fizista@gmail.com',
    maintainer='Wojciech Banaś',
    maintainer_email='fizista+umqtt.simple2@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    keywords='mqtt micropython',
    cmdclass={'sdist': SDistCommand, 'minify': PythonMinifier},
    setup_requires=['python_minifier'],
    packages=setuptools.find_packages('src'),
    package_dir={'': str(MINIFIED_DIR)},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    project_urls={
        'Bug Reports': 'https://github.com/fizista/micropython-umqtt.simple2/issues',
        'Source': 'https://github.com/fizista/micropython-umqtt.simple2',
    },
)
