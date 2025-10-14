import re

content = """
function scanFiles($dir, $opts=[])
{
    if (!file_exists($dir)) {
        return array();
    }
    $a = scandir($dir);
    $data = array();
    foreach ($a as $k => $v) {
        $path = $dir.'/'.$v;
        if ($v == '.' || $v == '..') {
            continue;
        }
        if ($opts['onlyDirs'] && !is_dir($path)) {
            continue;
        }
        if ($opts['onlyFiles'] && is_dir($path)) {
            continue;
        }
        if ($opts['utf']) {
            $path = iconv('windows-1251', 'utf-8', $path);
        }
        $data []= $path;
    }
    return $data;
}
"""



content = re.sub(r'function ([^{\n]+)\s*\{', r'def \g<1>:', content, re.I | re.U | re.S | re.M)
content = re.sub(r'if \(([^{]+)\)\s*\{', r'if \g<1>:', content, re.I | re.U | re.S | re.M)
content = re.sub(r'[}{$;]', '', content)
content = re.sub(r'\.', ' + ', content)
content = re.sub(r'\n\s*\n', "\n", content)
content = re.sub(r'array\(\)', "[]", content)
content = re.sub(r"echo ('[^\']+');", r'print(\g<1>)', content, re.I | re.U)
content = re.sub(r"echo ('.*?');", r'print(\g<1>)', content, re.I | re.U)
content = re.sub(r'foreach \(([a-z]+) as ([a-z]+)\)', r'for \g<2> in \g<1>:', content)
content = re.sub(r'foreach \(([a-z]+) as ([a-z]+) => ([a-z]+)\)', r'for \g<2>, \g<3> in \g<1>:', content)
print(content)