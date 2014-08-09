# -*- coding: utf-8 -*-
'''
#@summary: DbRowFactory is one common factory to convert db row tuple into user-defined class object.
           It is supported SqlAlchemy, and any database modules conformed to Python Database API
           Specification v2.0. e.g. cx_Oracle, zxJDBC
#@note:
   Note 1: The DbRowFactory will create one row instance based on row class binding,
        and try to assign all fields' value to the new object.
        The DbRowFactory maps field and class setter_method/attribute
        by matching names. If both a setter_method and an attribute match
        the same field, the setter_method will be chosen eventually.
        
   Note 2: __init__() of the class must no other arguments rather than self  
#@see: http://www.python.org/dev/peps/pep-0249/
#Tested under: Python 2.7, Jython2.5.2
#Change log:
    version 1.0.1, 09 Nov. 2011, initial version
    version 1.0.2, 16 Feb. 2012, use pyObjectCreator to instantiate rowClass
    version 1.0.3, 08 Mar. 2012, fromSqlAlchemyResultProxy(), fetchAllRowObjects() functions added
    version 1.0.4, 31 May. 2013, bug fixed version, disable auto-close cursor if not created by SqlAlchemy
    version 1.0.5, 04 Feb. 2014, import pyObjectCreator in explicit relative importing  
    
##====================sample begin=======
#sample code , file: OracleJdbcSample.py
from __future__ import with_statement
from com.ziclix.python.sql import zxJDBC
from pyDbRowFactory import DbRowFactory

class rowClass2(object):
    def __init__(self):
        self.owner=None
        self.tablename=None

    def setOWNER(self, value):
        self.owner=value

    def print2(self):
        print("ownerName="+self.owner+",tablename="+self.tablename)


if __name__=="__main__":

    #DB API 2.0 cursor sample
    jdbc_url="jdbc:oracle:thin:@127.0.0.1:1521:orcl";
    username = "user1"
    password = "pwd1"
    driver = "oracle.jdbc.driver.OracleDriver"
    with zxJDBC.connect(jdbc_url, username, password, driver) as conn:
        with conn.cursor() as cursor :
            cursor.execute("""select tbl.owner, tbl.table_name tablename,
            tbl.tablespace_name from all_tables tbl""")
            #use DbRowFactory to bind rowClass2 class defined in pkg1.OracleJdbcSample.py
            rowFactory=DbRowFactory(cursor, "pkg1.OracleJdbcSample.rowClass2")
            for rowObject in rowFactory.fetchAllRowObjects():
                rowObject.print2()



    #sqlalchemy sample
    from sqlalchemy import create_engine
    engine=create_engine("sqlite:///:memory:", echo=True)
    sql="""select tbl.owner, tbl.table_name tablename,
            tbl.tablespace_name from all_tables tbl"""
    resultProxy=engine.execute(sql)
    rowFactory=DbRowFactory.fromSqlAlchemyResultProxy(resultProxy, "pkg1.OracleJdbcSample.rowClass2")
    for rowObject in rowFactory.fetchAllRowObjects():
        rowObject.print2()

##====================sample end=======
'''
import inspect
import sys

__author__ = 'Harry Liu, <harrychinese@gmail.com>'
__version__= '1.0.5'


class DbRowFactory(object):
    '''
    #@summary: DbRowFactory is one common row factory for any database
               module conformed to Python Database API Specification
               v2.0. e.g. cx_Oracle, zxJDBC
    #@note: 
       Note 1: The DbRowFactory will create one row instance based on row class binding,
            and try to assign all fields' value to the new object.
            The DbRowFactory maps field and class setter_method/attribute
            by matching names. If both a setter_method and an attribute match
            the same field, the setter_method will be chosen eventually.
            
       Note 2: __init__() of the class must no other arguments rather than self  
               
    #@see: http://www.python.org/dev/peps/pep-0249/

    #@author: Harry Liu, harrychinese@gmail.com
    '''

    FIELD_TO_SETTER=1
    FIELD_TO_ATTRIBUTE=2
    FIELD_TO_NONE=0



    def __init__(self, cursor, rowClassFullName, setterPrefix="set", caseSensitive=False):
        '''
        ##@summary: Constructor of DbRowFactory
        [arguments]
        cursor: Db API 2.0 cursor object
        rowClassFullName: full class name that you want to instantiate, included package and module name if has
        setterPrefix: settor method prefix
        caseSensitive: match fieldname with class setter_method/attribute in case sensitive or not
        '''
        self._cursor=cursor
        self._setterPrefix=setterPrefix
        self._caseSensitive=caseSensitive

        self._fieldMemeberMapped=False
        self._allMethods=[]
        self._allAttributes=[]
        self._fieldMapList={}

        self._rowClassMeta = getClassMeta(rowClassFullName)
        self._resultProxy=None


    @classmethod
    def fromSqlAlchemyResultProxy(cls, resultProxy, rowClassFullName, setterPrefix="set", caseSensitive=False):
        '''
        ##@summary: another constructor of DbRowFactory
        [arguments]
        resultProxy: SqlAlchemyResultProxy object, can returned after engine.execute("select 1") called,
        rowClassFullName: full class name that you want to instantiate, included package and module name if has
        setterPrefix: settor method prefix
        caseSensitive: match fieldname with class setter_method/attribute in case sensitive or not
        '''
        factory= cls(resultProxy.cursor, rowClassFullName, setterPrefix, caseSensitive)
        factory._resultProxy=resultProxy
        return factory


    def createRowInstance(self, row ,*args,**kwargs):
        '''
        #@summary: create one instance object, and try to assign all fields' value to the new object
        [arguments]
        row: row tuple in a _cursor
        *args: list style arguments in class constructor related to rowClassFullName
        *kwargs: dict style arguments in class constructor related to rowClassFullName
        '''


        #step 1: initialize rowInstance before finding attributes.
        rowObject = self._rowClassMeta(*args,**kwargs)

        #mapping process run only once in order to gain better performance
        if self._fieldMemeberMapped==False:
            #dir() cannot list attributes before one class instantiation
            self._allAttributes=self._getAllMembers(rowObject)
            self._allMethods=self._getAllMembers(rowObject)
            self._fieldMapList=self._mapFieldAndMember()
            self._fieldMemeberMapped=True


        #step 2: assign field values
        i=0
        #self._fieldMapList is [{Field1:(member1Flag,member1)},{Field2:(member2Flag,member2)}]
        for fieldMemberDict in self._fieldMapList:
            for field in fieldMemberDict:
                member=fieldMemberDict[field]
                if member[0]==self.FIELD_TO_NONE:
                    pass
                else:
                    fieldValue=row[i]
                    if member[0]==self.FIELD_TO_SETTER:
                        m=getattr(rowObject, member[1])
                        m(fieldValue)
                    elif member[0]==self.FIELD_TO_ATTRIBUTE:
                        setattr(rowObject, member[1], fieldValue)

            i=i+1
        return rowObject


    def _getAllMembers(self,clazz) :
        '''
        #@summary: extract all user-defined methods in given class
        #@param param clazz: class object
        '''
        members=[member for member in dir(clazz)]
        sysMemberList=['__class__','__doc__','__init__','__new__','__subclasshook__','__dict__', '__module__','__delattr__', '__getattribute__', '__hash__', '__repr__', '__setattr__', '__str__','__format__', '__reduce__', '__reduce_ex__', '__sizeof__', '__weakref__']
        members=[member for member in members if str(member) not in sysMemberList]
        return members



    def _mapFieldAndMember(self):
        '''
        #@summary: create mapping between field and class setter_method/attribute, setter_method is preferred than attribute
        #field can be extract from cursor.description, e.g.
         sql: select 1 a, sysdate dt from dual
         cursor.description:
         [(u'A', 2, 22, None, 0, 0, 1), (u'DT', 91, 7, None, None, None, 1)]
        '''
        #print(self._cursor.description)
        fields=[f[0] for f in self._cursor.description]
        mapList=[]
        #result is [{Field1:(member1Flag,member1)},{Field2:(member2Flag,member2)}]
        for f in fields:
            m= self._getSetterMethod(f)
            key=f
            if m:
                value=(self.FIELD_TO_SETTER,m)
            else:
                m= self._getAttribute(f)
                if m:
                    value=(self.FIELD_TO_ATTRIBUTE,m)
                else:
                    value=(self.FIELD_TO_NONE,None)
            mapList.append({key:value})
        return mapList



    def _getAttribute(self, fieldName):
        '''
        #@summary: get related attribute to given fieldname
        '''
        if self._caseSensitive:
            if fieldName in self._allAttributes:
                return fieldName
        else:
            fieldNameUpper=fieldName.upper()
            allAttributesMap={}  # attributeUpper=attribute
            for attr in self._allAttributes:
                allAttributesMap[attr.upper()]=attr
            if fieldNameUpper in allAttributesMap:
                return allAttributesMap[fieldNameUpper]



    def _getSetterMethod(self, fieldName):
        '''
        ##@summary: get related setter method to given fieldname
        '''
        if self._caseSensitive:
            setter=self._setterPrefix+fieldName
            if setter in self._allMethods:
                return setter
        else:
            setterUpper=self._setterPrefix+fieldName
            setterUpper=setterUpper.upper()
            allMethodMap={}  # methodUpper=method
            for method in self._allMethods:
                allMethodMap[method.upper()]=method
            if setterUpper in allMethodMap:
                return allMethodMap[setterUpper]


    def _closeResultProxy(self):
        if self._resultProxy is not None:
            if self._resultProxy.closed==False:
                self._resultProxy.close()



    def _createdBySqlAlchemy(self):
        return self._resultProxy!=None


    def fetchAllRowObjects(self):
        """Fetch all rows, just like DB-API ``cursor.fetchall()``.
         the cursor is automatically closed after this is called
         """
        result=[]
        rows=self._cursor.fetchall()
        for row in rows:
            rowObject=self.createRowInstance(row)
            result.append(rowObject)

        if self._createdBySqlAlchemy():
            self._cursor.close()
            self._closeResultProxy()
        return result


    def fetchManyRowObjects(self, size=None):
        """Fetch many rows, just like DB-API
        ``cursor.fetchmany(size=cursor.arraysize)``.

        If rows are present, the cursor remains open after this is called.
        Else the cursor is automatically closed and an empty list is returned.

        """
        result=[]
        rows=self._cursor.fetchmany(size)
        for row in rows:
            rowObject=self.createRowInstance(row)
            result.append(rowObject)

        if self._createdBySqlAlchemy():
            if len(rows)==0:
                self._cursor.close()
                self._closeResultProxy()
        return result



    def fetchOneRowObject(self):
        """Fetch one row, just like DB-API ``cursor.fetchone()``.

        If a row is present, the cursor remains open after this is called.
        Else the cursor is automatically closed and None is returned.

        """
        result=None
        row = self._cursor.fetchone()
        if row is not None:
            result=self.createRowInstance(row)
        else:
            if self._createdBySqlAlchemy():
                self._cursor.close()
                self._closeResultProxy()

        return result





##reference doc
#http://www.cnblogs.com/sevenyuan/archive/2010/12/06/1898056.html
#http://stackoverflow.com/questions/4513192/python-dynamic-class-names
#http://stackoverflow.com/questions/1796180/python-get-list-of-al-classes-within-current-module


def createInstance(full_class_name,*args,**kwargs):
    '''
    instantiate class dynamically
    [arguments]
    full_class_name: full class name that you want to instantiate, included package and module name if has
    *args: list style arguments in class constructor
    *kwargs: dict style arguments in class constructor
    [return]
    an instance of this full_class_name
    [example]
    import pyObjectCreator
    full_class_name="knightmade.logging.Logger"
    logger=pyObjectCreator.createInstance(full_class_name,'logname')
    '''
    class_meta=getClassMeta(full_class_name)
    if class_meta!=None:
        obj=class_meta(*args,**kwargs)
    else:
        obj=None
    return obj


def getClassMeta(full_class_name):
    '''
    get class meta object of full_class_name, then we can use this meta object to instantiate full_class_name
    [arguments]
    full_class_name: full class name that you want to instantiate, included package and module name if has
    [return]
    an instance of this full_class_name
    [example]
    import pyObjectCreator
    full_class_name="knightmade.logging.Logger"
    loggerMeta=pyObjectCreator.getClassMeta(full_class_name)
    '''
    namespace=full_class_name.strip().rsplit('.',1)
    if len(namespace)==1:
        class_name=namespace[0]
        class_meta=_getClassMetaFromCurrModule(class_name)
    else:
        module_name=namespace[0]
        class_name=namespace[1]
        class_meta=_getClassMetaFromOtherModule(class_name,module_name)
    return class_meta


def _getClassMetaFromCurrModule(class_name):
    result=None
    module_name="__main__"
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isclass(obj):
            if name==class_name:
                result=obj
                break
    return result


def _getClassMetaFromOtherModule(class_name, module_name):
    module_meta=__import__(module_name,globals(), locals(),[class_name])
    if module_meta!=None:
        class_meta=getattr(module_meta,class_name)
    else:
        class_meta=None
    return class_meta