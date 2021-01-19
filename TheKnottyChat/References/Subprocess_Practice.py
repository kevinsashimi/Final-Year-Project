import subprocess
import os

from pathlib import Path


# subprocess.call("ipconfig", shell=True)

# output = subprocess.check_output('dir', shell=True, universal_newlines=True)
# print(output)

# Sets the stdout and stderr to the sub process pipe
# p1 = subprocess.run('dir', shell=True, capture_output=True)
# print(p1.stdout.decode('utf-8'))
#
# # Comes in as a string
# p2 = subprocess.run('dir', shell=True, capture_output=True, text=True)
# print(p2.stdout)
#
# # Redirects the stdout and stderr into pipe
# p3 = subprocess.run('dir', shell=True, stdout=subprocess.PIPE, text=True)
# print(p3.stdout)
#
# # Redirect output to a file
# with open('output.txt', 'w') as f:
#     p4 = subprocess.run('dir', shell=True, stdout=f, text=True)
#
# # Redirect the output of p5 into the input of p6
# # Note this is using windows commands
# p5 = subprocess.run('type output.txt', shell=True, capture_output=True, text=True)
# p6 = subprocess.run('findstr -i Subprocess_Practice.py', shell=True, capture_output=True, text=True, input=p5.stdout)
# print(p6.stdout)

# p7 = subprocess.run(["tree"], stdout=subprocess.PIPE, text=True)
# print(p7.returncode)

# Tree path traversal 1
def list_files():
    cwd = os.getcwd()
    tree_output = ''
    for root, dirs, files in os.walk(cwd):
        level = root.replace(cwd, '').count(os.sep)
        indent = ' ' * 4 * level
        tree_output += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            tree_output += f"{sub_indent}{f}\n"

    return tree_output


# Tree path traversal 2
class TreePath:
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last

        if self.parent:
            self.depth = self.parent.depth + 1

        else:
            self.depth = 0

    @property
    def display_name(self):
        if self.path.is_dir():
            return self.path.name + '/'

        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path for path in root.iterdir() if criteria(path)), key=lambda s: str(s).lower())
        count = 1

        for path in children:
            is_last = count == len(children)

            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)

            else:
                yield cls(path, displayable_root, is_last)

            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def display__name(self):
        if self.path.is_dir():
            return self.path.name + '/'

        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.display_name

        filename_prefix = (self.display_filename_prefix_last if self.is_last else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(filename_prefix, self.display_name)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle if parent.is_last else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


if __name__ == '__main__':
    output1 = list_files()
    output2 = ''
    paths = TreePath.make_tree(Path(str(os.getcwd())))
    for p in paths:
        output2 += (p.displayable() + '\n')

    print(output1)
    print(output2)
