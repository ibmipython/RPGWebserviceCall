from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import requests
from string import Template
import time
import xml.etree.ElementTree as ET
import csv
#import pdb

numberOfrows = 0
inputFile = 'files/SomeCSVFile.csv'
output = 'files/ProcessedOutput.txt'
errorFile = 'files/ErrorOutPut.txt'

#This is the connection name that you will be making
url = "?WSDL"

#used to determine number of rows in the csv. Which can be used in your concurrent.futures to establish a number of threads
with open(inputFile, 'r') as counter:
    csvReader = csv.reader(counter)
    next(csvReader)
    numberOfrows = sum(1 for row in csvReader)
    Threads = numberOfrows/1000

# below template will contain the request structure, the request the web service is expecting. Soap Message for simple terms
messagetemplate = Template(r"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:gsd="http://serviceName.wsbeans.iseries/">
   <soap:Header/>
   <soap:Body>
      <gsd:IBMIWebserice>
         <arg0>
            <p_XMLIN>
               <length>15000</length>
               <string>
               <![CDATA[<input>
                    <name>SomePRocess</name>
                    <detail>$detail</detail>
                    <email>$email</email>
               </input>]]>
               </string>
            </p_XMLIN>
            <p_XMLOUT>
               <length>0</length>
               <string></string>
            </p_XMLOUT>
         </arg0>
      </gsd:IBMIWebserice>
   </soap:Body>
</soap:Envelope>""")

#don't forget to add your headers
headers = {'SOAPAction': 'process', 'Content-Type': 'text/xml;charset=UTF-8'}

#create a function which receives parameters and handle the call to the web service
def action_post_request(url,data,timeout,responses):
    response = requests.post(url,data = data, timeout = timeout, headers=headers)
    responses = response
    return {'response':response}

#this function will handle the writting instructions to your output files
def write(text,filename):
    file = open(filename, 'a')
    file.write(text)
    file.close()

#with will handle the opening and closing of your CSV, Passing 'r' will only allow you to read to from the CSV
with open(inputFile,'r') as csvFile:
    csvReader = csv.reader(csvFile)
    next(csvReader)
    future_to_line ={}
    #pdb.set_trace()

    #read each line in the CSV
    for line in csvReader:
         #need to do the below for every field per row in the CSV if you want to use all comma separated values
         detailrec = line[0]
         emailrec = line[1]
         detailrec = line[0]
         emailrec = line[1]
         policyNorec = line[2]
         postItrec = line[3]
         responses = ''
         endtime = ''
         #calling the substitute function for messageTemplate will find your $field
         # and replace it with the variable value assigned to it
         data = messagetemplate.substitute(detail=detailrec, email=emailrec)
         action_post_request(url, data,60,responses)
         try:
            #testing for a response. In this case i won't be getting a response to process from the web service
            if not responses:
               times = time.gmtime()
               write(policyNorec+' : '+'Success : EndTime : '+ time.strftime("%Y-%m-%d %H:%M:%S",times)  +"\n",output)   
         except Exception as exc:
            write(policyNorec+' : '+str(exc)+"\n",errorFile)            
       
