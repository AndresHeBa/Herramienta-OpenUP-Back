from datetime import datetime
import BackEnd.GlobalInfo.ResponseMessages as ResponseMessage
import BackEnd.GlobalInfo.Helpers as HelperFunctions

dbConnLocal = None
try:
    dbConnLocal = HelperFunctions.dbConnection()
except Exception:
    dbConnLocal = None

# In-memory stores for testing
_TEST_CASES_STORE = []
_TEST_EXECUTIONS_STORE = []

def _use_db():
    return dbConnLocal is not None


def fnCreateTestCase(projectId, name, description, artifactId, artifactName, preconditions, steps, expectedResult, priority, createdBy):
    try:
        test_case = {
            "projectId": projectId,
            "name": name,
            "description": description,
            "artifactId": artifactId,
            "artifactName": artifactName,
            "preconditions": preconditions,
            "steps": steps,  # Lista de {stepNumber, action, expectedResult}
            "expectedResult": expectedResult,
            "priority": priority,
            "createdBy": createdBy,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        if _use_db():
            result = dbConnLocal.clTestCases.insert_one(test_case)
            test_case["_id"] = str(result.inserted_id)
        else:
            test_case["_id"] = str(len(_TEST_CASES_STORE) + 1)
            _TEST_CASES_STORE.append(test_case)
        
        return {**ResponseMessage.message200, "data": test_case}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetTestCasesByProject(projectId):
    try:
        if _use_db():
            test_cases = list(dbConnLocal.clTestCases.find({"projectId": projectId}))
            for tc in test_cases:
                tc["_id"] = str(tc["_id"])
            return {**ResponseMessage.message200, "data": test_cases}
        else:
            test_cases = [tc for tc in _TEST_CASES_STORE if tc["projectId"] == projectId]
            return {**ResponseMessage.message200, "data": test_cases}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnExecuteTestCase(testCaseId, projectId, executedBy, status, actualResult, evidence, notes, iteration):
    try:
        execution = {
            "testCaseId": testCaseId,
            "projectId": projectId,
            "executedBy": executedBy,
            "executedAt": datetime.now(),
            "status": status,  # Pasó, Falló, Bloqueado, No Ejecutado
            "actualResult": actualResult,
            "evidence": evidence,
            "notes": notes,
            "iteration": iteration,
            "defectIds": []
        }
        
        if _use_db():
            result = dbConnLocal.clTestExecutions.insert_one(execution)
            execution["_id"] = str(result.inserted_id)
        else:
            execution["_id"] = str(len(_TEST_EXECUTIONS_STORE) + 1)
            _TEST_EXECUTIONS_STORE.append(execution)
        
        return {**ResponseMessage.message200, "data": execution}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetTestExecutionsByProject(projectId):
    try:
        if _use_db():
            executions = list(dbConnLocal.clTestExecutions.find({"projectId": projectId}))
            for ex in executions:
                ex["_id"] = str(ex["_id"])
            return {**ResponseMessage.message200, "data": executions}
        else:
            executions = [ex for ex in _TEST_EXECUTIONS_STORE if ex["projectId"] == projectId]
            return {**ResponseMessage.message200, "data": executions}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500


def fnGetTestExecutionsByTestCase(testCaseId):
    try:
        if _use_db():
            executions = list(dbConnLocal.clTestExecutions.find({"testCaseId": testCaseId}))
            for ex in executions:
                ex["_id"] = str(ex["_id"])
            return {**ResponseMessage.message200, "data": executions}
        else:
            executions = [ex for ex in _TEST_EXECUTIONS_STORE if ex["testCaseId"] == testCaseId]
            return {**ResponseMessage.message200, "data": executions}
    
    except Exception:
        HelperFunctions.PrintException()
        return ResponseMessage.message500
