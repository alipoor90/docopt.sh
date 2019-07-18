from .doc_ast import Option, Command, Required, Optional, OptionsShortcut, OneOrMore, Either
from .bash import Code, bash_variable_name, bash_variable_value, bash_ifs_value

helper_map = {
  Required: 'required',
  Optional: 'optional',
  OptionsShortcut: 'optional',
  OneOrMore: 'oneormore',
  Either: 'either',
}


class Node(Code):

  def __init__(self, pattern, body, idx):
    self.pattern = pattern
    self.idx = idx
    code = '{name}(){{\n{body}\n}}\n'.format(
      name='node_' + str(idx),
      body=body,
    )
    super(Node, self).__init__(code)


class BranchNode(Node):

  def __init__(self, pattern, idx, node_map):
    # minify arg list by only specifying node idx
    child_indexes = map(lambda child: node_map[child].idx, pattern.children)
    body = '  {helper} {args}'.format(
      helper=helper_map[type(pattern)],
      args=' '.join(list(map(str, child_indexes))),
    )
    super(BranchNode, self).__init__(pattern, body, idx)


class LeafNode(Node):

  def __init__(self, pattern, idx):
    default_value = pattern.value
    if type(pattern) is Option:
      helper_name = 'switch' if type(default_value) in [bool, int] else 'value'
      needle = idx
    elif type(pattern) is Command:
      helper_name = '_command'
      needle = pattern.name
    else:
      helper_name = 'value'
      needle = 'a'
    self.variable_name = bash_variable_name(pattern.name)

    args = [self.variable_name, bash_ifs_value(needle)]
    if type(default_value) in [list, int]:
      args.append(bash_ifs_value(True))
    elif helper_name == '_command' and args[0] == args[1]:
      args = [args[0]]
    body = '  {helper} {args}'.format(
      helper=helper_name,
      args=' '.join(args),
    )

    if type(default_value) is list:
      default_tpl = (
        'if declare -p {docopt_name} >/dev/null 2>&1; then\n'
        '  eval "${{prefix}}"\'{name}=("${{{docopt_name}[@]}}")\'\n'
        'else\n'
        '  eval "${{prefix}}"\'{name}={default}\'\n'
        'fi'
      )
    else:
      default_tpl = (
        'eval "${{prefix}}"\'{name}=${{{docopt_name}:-{default}}}\''
      )
    self.default_assignment = default_tpl.format(
      name=self.variable_name,
      docopt_name='var_' + self.variable_name,
      default=bash_variable_value(default_value)
    )
    self.prefixed_variable_name = '${{prefix}}{name}'.format(name=self.variable_name)
    super(LeafNode, self).__init__(pattern, body, idx)
