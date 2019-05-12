from .. import Function


class Main(Function):
  def __init__(self, settings):
    super(Main, self).__init__(settings, 'docopt')

  @property
  def body(self):
    body = '''
type check &>/dev/null && check
setup "$@"
parse_argv
extras
local i=0
while [[ $i -lt ${#parsed_params[@]} ]]; do
  left+=("$i")
  ((i++))
done
if ! root || [ ${#left[@]} -gt 0 ]; then
  error
fi
type defaults &>/dev/null && defaults
type teardown &>/dev/null && teardown
return 0
'''
    return body
