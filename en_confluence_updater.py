"""

This Script updates Confluence page with the data provided as args.
Usage:  written in usage() below.

# Author: Vamsi Krishna Lella
# Email : vamsikrishna.naidu@gmail.com
# Dated : 15th May 2018. 

"""

import re, sys, ast, json, argparse, requests

url = "https://localhost:8080/rest/api/content/"
user_name = "conf_bot"
passowrd = "conf_123@123"
ERR_INVALID_ARGS = 1


def usage():
  """
  Prints the usage of the script
  """
  print """
  --pageId < PageId >
  --updateTable < updateTable Content >
  --updateEntire < updateEntire Page >

  eg: ./confluence.py --pageId 221872136 --updateTable "" --updateEntire ""
     
     --updateTable " table values to be updated. as an array " 

     eg: --updateTable '["test1", "10 passed", "2 failed", "test2", "10 passed", "2 failed"]'
     
     --updateEntire " content of the page to be updated ( entire page will be updated.) "
  """


def update_page(page_id, data):
  headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
  try:
    response = requests.put(url + page_id, headers = headers, data = data, auth = (user_name, passowrd))
    code = response.status_code
    if code == 200:
      print " !!! Page Updated Successfully... !!! Status code = " + str(code)
    else:
      print " !!! Something Went Wrong !!! Status code = " + str(code)
  except Exception as e:
    print " !!! in Exception !!! "
    print e


def replace_every_occurance(result__, sub, rsub, occurance_):
  pos__ = [m.start() for m in re.finditer(sub, result__)][occurance_ - 1]
  b_string = result__[:pos__]
  a_string = result__[pos__:]
  a_string = a_string.replace(sub, rsub, 1)
  result__ = b_string + a_string
  return result__

def get_page_json(page_id, update_table, update_entire, check_):
  response, content__ = "", ""
  final_url = url + page_id
  if check_:
    final_url = final_url + "?expand=body.storage"
  response = requests.get(final_url, auth = (user_name, passowrd))   
  if response.status_code == 200:
    result__ = response.text.encode("utf-8")
    if check_:
      count__ = result__.count("<td>")
      update_table = ast.literal_eval(update_table)
      len_ut = len(update_table)
      if count__ == len_ut:
        for i in range(len_ut):
          result__ = replace_every_occurance(result__, "<td>", "<td>" + update_table[i], i+1)
        final_body_content = json.loads(result__)["body"]
        response = requests.get(url + page_id, auth = (user_name, passowrd))
        result__ = response.text.encode("utf-8")
        result__ = json.loads(result__)
        result__["body"] = final_body_content
        result__ = json.dumps(result__)
      else:
        print " !!! Page contains " + str(count__) + " table fields, and you have passed " + str(len_ut) + ",  pelase pass the correct no.of fields data. !!! "
        sys.exit(ERR_INVALID_ARGS)
    else:
      content__ = '{"body":{"storage":{"value":"' + update_entire + '", "representation": "storage"}},'
      result__ = result__.replace("{", content__, 1)
    version_string = re.search(r'number[\'|"]:(\s*|)\d*', result__).group()
    if version_string:
      res = json.loads(response.text)
      version = str(res["version"]["number"] + 1)
      result__ = result__.replace(version_string, ('number":' + '"' + version + '"'))
    update_page(page_id, result__)
  else:
    print " !!! Something went wrong. stauts code = " + str(response.status_code) + " !!!"
    try:
      res = json.loads(response.text)
      print res["message"]
    except Exception as e:
      print re.search(r'<h1>\w.*</h1>', response.text).group()


def required_args():
  print "\n !!! Please pass the required Arguments !!! "
  usage()
  sys.exit(ERR_INVALID_ARGS)


def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('--pageId',  required = True, help = " Provide Page id for updating. ")
  arg_parser.add_argument('--updateTable', required = True, help = " Table content to be supplied as a string of list. ")
  arg_parser.add_argument('--updateEntire', required = True, help = " page Content to be Updated. ")
  args = arg_parser.parse_args()
  if args.pageId.strip() == "" and (args.updateEntire.strip() == "" or args.updateTable.strip() == ""):
    required_args()
  check_ = True if args.updateTable.strip() != "" else False
  get_page_json(args.pageId, args.updateTable, args.updateEntire, check_)

if __name__ == '__main__':
  main()
