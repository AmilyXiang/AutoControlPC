import xml.etree.ElementTree as ET
import os

def parse_testcases(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for testcase in root.findall('testcase'):
        print(f"用例: {testcase.get('name')}")
        for step in testcase.findall('step'):
            step_type = step.get('type')
            action = step.get('action')
            content = step.get('content')
            print(f"  步骤: type={step_type}, action={action}, content={content}")

if __name__ == '__main__':
    xml_file = os.path.join(os.path.dirname(__file__), 'testcase', 'testcases.xml')
    parse_testcases(xml_file)
