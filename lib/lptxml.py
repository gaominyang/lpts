# -*- coding:utf-8 -*-
# filename: lptxml.py

'''
'''

from lpt.lib.share import base_xml
import os, sys
from lpt.lib import readconfig
from lpt.lib import lptlog
from lpt.lib.error import *
from lpt.lib.share import utils
import datetime
from lpt.lib import lmbench

LPTROOT = os.getenv('LPTROOT')
PARAMETER_FILE = os.path.join(LPTROOT, 'config/parameter.conf')
DB_DIR = os.path.join(LPTROOT, 'db')
JOBS_XML = os.path.join(DB_DIR, 'jobs.xml')

JOB_ELEMENT = '''
<job, jobid= %s>
        <tools>%s</tools>
        <resultsdb>%s</resultsdb>
        <parameter_md5>%s</parameter_md5>
</job> 
''' 

INDEX_KEYS = {'unixbench':['Dhrystone2-using-register-variables',
                    'Double-Precision-Whetstone',
                    'Execl-Throughput',
                    'FileCopy1024-bufsize2000-maxblocks',
                    'FileCopy256-bufsize500-maxblocks',
                    'FileCopy4096-bufsize8000-maxblocks',
                    'Pipe-Throughput',
                    'Pipe-based-ContextSwitching',
                    'Process-Creation',
                    'ShellScripts-1concurrent',
                    'ShellScripts-8concurrent',
                    'System-Call-Overhead',
                    'System-Benchmarks-Index-Score'],
        'x11perf':['aa-polygon',
                        'ellipses',
                        'images-and-blits',
                        'rectangles',
                        'text',
                        'windows'
                        #'Graphics-Benchmarks-Index-Score'
                            ],
        'glxgears':['gears'],
        'stream':['Copy', 'Add', 'Triad', 'Scale'],
        'pingpong':["initialised", "completed", "total"],
        'iozone':['write', 'rewrite', 'read', 'reread', 'randread', 'randwrite'],
        'bonnie':["putc","putc_cpu","put_block","put_block_cpu","rewrite","rewrite_cpu",
                "getc","getc_cpu","get_block","get_block_cpu","seeks","seeks_cpu","seq_create",
                "seq_create_cpu","seq_stat","seq_stat_cpu","seq_del","seq_del_cpu","ran_create","ran_create_cpu",
                "ran_stat","ran_stat_cpu","ran_del","ran_del_cpu" ],
        'dbench_fio':['Throughtput', 'max_latency'],
        'lmbench':lmbench.get_index_list()
        }
class ConfigToXml(readconfig.BaseConfig, base_xml.RWXml):
    '''
    ????????????ConfigParser???????????????xml??????
    '''
    def __init__(self, config_file, xml_file ):
        #super(ConfigToXml, self).__init__(config_file, xml_file)
        readconfig.BaseConfig.__init__(self, config_file)
        base_xml.RWXml.__init__(self, xml_file)
        
         # define:????????????section
        self.custom_sections = None
        
    def add_test_group(self, test_list):
        '''
        ??????????????????
        '''
        if isinstance(test_list, list)  and test_list:
            self.custom_sections = test_list
        else:
            #self.custom_sections = self.get_sections()  #????????????
            #lptlog.error("????????????????????? ????????????????????????")
            raise CreateJobException("????????????????????? ????????????????????????")
        return 
        
    def add_configparser_node(self, father_node, node_tag, node_attrib):
        '''
        ???father_node???????????????ParserConfig???????????????
        @param fathor_node:?????????
        @param node_tag: ????????????
        @param node_attrib: ????????????
            '''
            
        sections = self.custom_sections
        lptlog.info('??????????????????%s' % ' ,'.join(sections))
        for section in sections:
            subnode = self.create_node(node_tag, dict({'id':section}, **node_attrib))
            self.add_node(father_node, subnode)
            options = self.get_options(section)
            for option in options:
                value = self.get_str_value(section, option)
                self.create_element(subnode, option, value)
                
        
    def transfer(self, root_tag, father_node_tag, node_tag, node_attrib):
        '''
        ???ParserConfig?????????????????????????????????
        
        @param root_tag: 
        @param father_node_tag: 
        @param node_tag: 
        @param node_attrib: ??????
        '''
         #??????self.tree????????????
        if not self.tree:
            self.create_tree()
            
        #???????????????
        root = self.create_root_node(root_tag)
        #???????????????
       
        father_node = self.create_node(father_node_tag)  
        self.add_node(root, father_node)
        self.add_configparser_node(father_node, node_tag, node_attrib)
        
        #save to xml
        self.save_file()


def config_to_xml(config_file, xml_file, root_tag, father_node_tag, node_tag, node_attrib, test_list):
    '''
    ??????ParserConfig?????????????????????xml?????????xml?????????3
    @param config_file:ParserConfig????????????
    @param xml_file: ?????????xml?????????
    @param root_tag: ???????????????
    @param father_node_tag: ???????????????
    @param node_attrib: ???????????? 
    @param test_list: ????????????
    '''
    
    confxml = ConfigToXml(config_file, xml_file)
    
    if node_attrib is None:
        node_attrib = {}
    if test_list is not None:
        confxml.add_test_group(test_list)
    confxml.transfer(root_tag, father_node_tag, node_tag, node_attrib)
    

class Jobs(base_xml.RWXml):
    '''create jobs.xml
    '''
    def __init__(self, xml_file=JOBS_XML):
        super(Jobs, self).__init__(xml_file)
        
        #?????????
        if not os.path.exists(self.xml_file):
            if  self.tree is None:
                self.create_tree()
                
                #???????????????
            self.root = self.create_root_node('jobs')
    
        else:
            self.init_tree()
            self.root = self.get_root()
            
    def create_job(self, tools_list, parameter, job_attrib={}, resultXmlName="results"):
        '''??????jobs.xml??????
        '''
        DateString = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        #results = 'result_%s.xml' % DateString
        results = '%s_%s.xml' % (resultXmlName, DateString)
        
        job = self.create_node('job', dict({'id':DateString, 'status':"N/A"}, **job_attrib))
        lptlog.info('??????ID: %s' % DateString)
        
        self.create_element(job, 'resultsDB', results)
        lptlog.info('xml results??????:  %s' % results)
        
        lptlog.debug("????????????")
        conftoxml = ConfigToXml(parameter, self.xml_file)
        conftoxml.add_test_group(tools_list)
        try:
            conftoxml.add_configparser_node(job, 'tool', {'status':'no'})
        except Exception as e:
            #lptlog.exception('parameter.conf??????xml??????')
            #lptlog.error('parameter.conf??????xml??????')
            raise CreatNodeError('parameter.conf??????xml??????: %s' % e)
        
        if job is None:
            raise CreatJobsError()
        else:
            return job
        
    def add_job(self, job_node):
        '''
        '''
        #??????job??????????????????
        self.add_node(self.root, job_node )
        
        #???????????????
        self.save_file()
    
    def get_new_job(self):
        '''
        @return: ??????????????????job???IndexError
        '''
        return self.root[-1]
    

    def search_job_node(self, match_tag):
        '''
        ????????????????????????node???None
        '''
        return self.find_node_by_tag(self.root, match_tag)
    
    def search_job_nodes(self, match_tag):
        '''
        ?????????????????????nodes???None
        '''
        return self.find_nodes_by_tag(self.root, match_tag)
    
    
    def search_job_texts(self, element_tag):
        '''
        ?????????????????????text???None
        @attention: element_tag,??????job_tag?????????job/results
        @return: text,type list 
        '''
        return self.find_texts_by_tag(self.root, element_tag)
    
    def get_job_text(self, job_node, element_tag):
        '''
        ??????job?????????tag???text
        '''
        element = self.find_node_by_tag(job_node, element_tag)
        return self.get_element_text(element)
    
    def get_tools_nodes(self, job_node):
        '''
        ???????????????????????????
        @return: node list or None
        '''
        tools_nodes_list = self.find_nodes_by_tag(job_node, 'tool')
        
        return tools_nodes_list
    
    def get_noexec_tools_nodes(self, job_node):
        '''@return: list 
        '''
        #python 2.7
        #return job_node.findall("tool[@status='no']")
        #python 2.6
        return   [x for x in job_node.findall("tool") if x.get('status')=='no']
    
    def get_tool_attrib(self, tool_node, key):
        return self.get_node_attrib_value(tool_node, key)
    
    def get_tool_name(self, tool_node):
        return self.get_node_attrib_value(tool_node, 'id')
    
    
    #def get_job_test_status(self, tool_node):
       # '''??????????????????????????????ok or no
        #'''
       # return self.get_node_attrib_value(tool_node, 'status')
    
    def get_tool_status(self, tools_nodes, tool):
        '''
        ???????????????????????????
        @param tools_nodes: ??????????????????
        @param tool: ????????????
        @return: 'ok' ??? ' no' or None
        '''

        for node in tools_nodes:
            if self.get_node_attrib_value(node, 'id') == tool:
                return self.get_node_attrib_value(node, 'status')
            else:
                continue
    
    def set_tool_status(self, tool_node, status='ok'):
        '''
        ??????????????????????????????????????????
        '''
        self.modefy_node_attrib_value(tool_node, 'status', status)
        
    def get_tool_text(self, tool_node, element_tag):
        '''
        @return: ???????????????element_tag ???????????????
        '''
        element = self.find_node_by_tag(tool_node, element_tag)
        return self.get_element_text(element)
    
  
def add_job(xml_file, tools_list, parameter, job_attrib={}, resultXmlName="results"):
    '''?????????????????????xml_file??????
    @param xml_file: ??????????????????
    @param tools_list:????????????
    @type tools_list: list 
    '''
    #???????????????
    jobs = Jobs(xml_file)
    job = jobs.create_job(tools_list, parameter, job_attrib=job_attrib, resultXmlName=resultXmlName)
    #??????job
    jobs.add_job(job)

def search_job_node(node_tag, xml_file=JOBS_XML):
    #???????????????
    jobs = Jobs(xml_file) 
    return jobs.search_job_node(node_tag)

def search_job_nodes(node_tag, xml_file=JOBS_XML):
    #???????????????
    jobs = Jobs(xml_file) 
    return jobs.search_job_nodes(node_tag)

def get_job_text(element_tag, xml_file=JOBS_XML, job_node=None):
    '''??????xml_file???job???????????????????????????????????????job
    @param job_tag: ?????????element?????????
    @return: ??????text
    '''
   #???????????????
    jobs = Jobs(xml_file)
    if job_node is None:
        job_node = jobs.get_new_job()
        
    return jobs.get_job_text(job_node, element_tag)

def get_job_attrib_value(key, xml_file=JOBS_XML, job_node=None):
    '''??????xml_file???job?????????????????????????????????job
    @param key: ?????????key?????????
    @return: ??????string
    '''
    #???????????????
    jobs = Jobs(xml_file)
    if job_node is None:
        job_node = jobs.get_new_job()
    
    return job_node.get(key)

def search_job_texts(element_tag, xml_file=JOBS_XML):
    '''??????element_tag?????????value
    '''
    #???????????????
    jobs = Jobs(xml_file)
    return jobs.search_job_texts(element_tag)

def get_tools_nodes(job_node, jobs_xml=JOBS_XML):
    '''get all nodes under job_node
    '''
    jobs = Jobs(jobs_xml)
    return jobs.get_tools_nodes(job_node)

def get_tool_node(tool, jobs_xml=JOBS_XML, job_node=None):
    '''??????????????????
    '''
    jobs = Jobs(jobs_xml)
    if job_node is None:
        job_node = jobs.get_new_job()
   #python 2.7
   # return job_node.find("tool[@id='%s']" % tool)
   #python 2.6
    return [x for x in jobs.get_tools_nodes(job_node) if x.get('id')==tool][0]

        
def get_job_result_file(jobs_xml=JOBS_XML, job_node=None):
    '''
    ????????????job???????????????
    '''
    result_xml = get_job_text('resultsDB', jobs_xml, job_node)
    result_xml_abspath = os.path.join(DB_DIR, result_xml)
    return result_xml_abspath

    
def get_tool_parameter(tool_node, element_tag, xml_file=JOBS_XML):
    '''??????????????????
    @param xml_file: jobs????????????
    @param tool_node: ????????????
    @param element_tag: ????????????
    @return: ??????value
    '''
    jobs = Jobs(xml_file)
    return jobs.get_tool_text(tool_node, element_tag)
    #return jobs.find_text_by_tag(tool_node, element_tag)
    
class XmlResults(base_xml.RWXml):
    '''
    ???????????????????????????xml??????
    '''
    def __init__(self, xml_file):
        super(XmlResults, self).__init__(xml_file)
      
        #?????????
        if not os.path.exists(self.xml_file):
            #if  self.tree is None:
            if not self.tree:
                self.create_tree()
                
             #???????????????
            from lpt.lib import sysinfo
            self.root_attrib = sysinfo.OSInfo.keys
            self.root = self.create_root_node('results', self.root_attrib)
    
        else:
            self.init_tree()
            self.root = self.get_root()

    #def _get_root_attrib(self):
     #  for subdic in sysinfo.OSysinfo.keys.itervalues():
      #      root_dic = dict(root_dic, **subdic)
       # return root_dic
    
  
    def save_result_node(self, result_node_tag, result_node_attrib, result_list, **kwargs):
        '''
        result_list = [ [{}, {}], [{},{}] ]
        ?????????????????????????????????
        ?????????list??????????????????????????????dict????????????????????????????????????????????????dict???????????????
        @param result_node_tag: ?????????????????????
        @param result_node_attrib: ?????????????????????
        @param result_list: ????????????????????????: [ [{}, {}], [{},{}] ]
        '''
    
        for result_list_one in result_list:
            result_node = self.create_node(result_node_tag, dict(result_node_attrib, **result_list_one[0]))
            #???????????????????????????????????????????????????????????????unixbench?????????????????????????????????key??????????????????????????????????????????????????????
            if result_node_tag in list(INDEX_KEYS.keys()):
                keys = INDEX_KEYS.get(result_node_tag)
            else:
                keys = list(result_list_one[1].keys())
        
            for key in keys:
                self.create_element(result_node, key, result_list_one[1][key])
            self.add_node(self.root, result_node)
       
        self.save_file()
        
    def get_result_tools(self):
        ''' ??????????????????'''
        tools = [x.tag for x in list(self.root)]
        #????????????
        return list({}.fromkeys(tools).keys())
    
    def search_tool_result_nodes(self, tool_name):
        '''??????nodes(list)???None
        '''
        return self.find_nodes_by_tag(self.root, tool_name)
    
    def get_tool_element_tag(self, node):
        '''
        @return: list, get all element tag
        '''
        return [x.tag for x in self.get_elements(node)]
    
    def get_tool_result_parallels(self, tool_name, key='parallels'):
        '''?????????????????????
        @return: None???value(string)
        '''
        tool_nodes = self.search_tool_result_nodes(tool_name)
        return self.get_node_attrib_value(tool_nodes[0], key)
    
    def search_tool_result_parallel_nodes(self, tool_name, parallel):
        '''??????nodes???None
        '''
        #python 2.7
        #return self.find_nodes_by_tag(self.root, "./%s[@parallel='%s']" % (tool_name, parallel))
        #python 2.6
       # print map(lambda x:x.get("parallel"), self.find_nodes_by_tag(self.root, "%s" % tool_name))
        return [x for x in self.find_nodes_by_tag(self.root, "%s" % tool_name) if x.get("parallel")==str(parallel)]
    
    
    def search_tool_result_by_elementTag(self, tool_name, elementTag):
        '''
        @return: return all elements by tag
        '''
        return self.find_elements_by_tag(self.root, "%s/%s" % (tool_name, elementTag))
    
    def search_element_by_tagAndtimes(self, tool, element_tag, parallel, times):
        '''
        @attention: ?????????????????????
        @return: list
        '''
        #python 2.7
        #return self.find_text_by_tag(self.root, "%s[@iter='%s'][@parallel='%s']/%s" % (tool, times, parallel, element_tag))
        #python 2.6
        match_nodes = [x for x in self.find_nodes_by_tag(self.root, tool) if x.get("parallel")==str(parallel) and x.get("iter")==str(times)]
        return [self.find_text_by_tag(y, element_tag) for y in match_nodes]
    
    
    def search_nodes_by_parallelAndtimes(self, tool, parallel, times):
        #python 2.6
        match_nodes = [x for x in self.find_nodes_by_tag(self.root, tool) if x.get("parallel")==str(parallel) and x.get("iter")==str(times)]
        return match_nodes
    
    
    def get_result_text(self, result_node, element_tag):
        '''
        @param result_node: result??????
        @param element_tag: ????????????
        @return: text??????None
        '''
        element = self.find_node_by_tag(result_node, element_tag)
        return self.get_element_text(element)
    
    def get_result_attrib(self, result_node, key):
        '''@param key: node attrib 
        '''
        return self.get_node_attrib_value(result_node, key)
        
def get_result_tools(resultDB):
    '''??????resultDB?????????????????????
    '''
    xmlresult = XmlResults(resultDB)
    return xmlresult.get_result_tools()

def get_result_parallels(resultDB, tool):
    xmlresult = XmlResults(resultDB)
    return xmlresult.get_tool_result_parallels(tool)



  

    
    
    
    
