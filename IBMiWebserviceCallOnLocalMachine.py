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
with open(inputFile,'r') as counter:
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
headers = {'SOAPAction': 'process','Content-Type':'text/xml;charset=UTF-8'}

#create a function which receives parameters and handle the call to the web service
def action_post_request(url,data,timeout):
    startTime = time.time()
    response = requests.post(url,data = data, timeout = timeout, headers=headers)
    endTime = time.time() - startTime
    return {'responsetime':endTime,'response':response}

#this function will handle the writting instructions to your output files
def write(text,filename):
    file = open(filename, 'a')
    file.write(text)
    file.close()

#the below is tha main logic where all your magic will be happening
#threadPool is where you assign your number of threads you want to use, the above code where I determined 
# the number of rows in the CSV can but used by your own discretion.
#Do a simple divition on the number to determineyour thread count. which will then look like this:
#with ThreadPoolExecutor(max_workers=Threads) as executor:
with ThreadPoolExecutor(max_workers=5) as executor:
    #with will handle the opening and closing of your CSV, Passing 'r' will only allow you to read to from the CSV
    with open(inputFile,'r') as csvFile:
        csvReader = csv.reader(csvFile)
        next(csvReader)
        futureLine ={}
        #uncomment the trace below if you want to perform a debug
        ##pdb.set_trace()

        #read each line in the CSV
        for line in csvReader:
            #need to do the below for every field per row in the CSV if you want to use all comma separated values
            detailrec = line[0]
            emailrec = line[1]
            #calling the substitute function for messageTemplate will find your $field 
            # and replace it with the variable value assigned to it
            data = messagetemplate.substitute(detail=detailrec,email=emailrec)
            #this will be submitting your request into threads
            futureLine[executor.submit(action_post_request,url, data,60)]=emailrec
            #as the threads complete you will be need to handle the response back from the web service if you are posting back
            for future in as_completed(futureLine):
                process_name_from_future = futureLine[future]
                try:
                    #the web service calling function above returns the data in a dictonary and you are looking for the response
                    # if you want the response time you will then pass responsetime instead of response
                    data = future.result()['response']
                except Exception as exc:
                    write(process_name_from_future+' : '+str(exc)+"\n",errorFile)
                else:
                    try:
                        #just storing the post back from the web service but you will need to handle it if you 
                        # are receiving a response which you want to perform a certain actoin for
                        xml=ET.fromstring(data.text)
                        write(process_name_from_future+" : "+str(xml.text)+"\n",output)                     

                    except Exception as exc:
                        write(process_name_from_future + ' : ' + str(exc) + "\n",errorFile)
