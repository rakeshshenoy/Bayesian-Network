#!/usr/bin/python
from decimal import Decimal
import sys
import copy
import string
import itertools

def writeToFile(line):
    output = open('output.txt', 'a')
    output.write(str(line) + '\n')
    output.close()

def calcProb(bn, Y, e):
    if bn[Y]['prob'] == 1.0:
        return 1.0
    if bn[Y]['prob'] != -1:
        prob = bn[Y]['prob'] if e[Y] else 1 - bn[Y]['prob']
    else:
        parents = tuple(e[p] for p in bn[Y]['parents'])
        prob = bn[Y]['condProb'][parents] if e[Y] else 1 - bn[Y]['condProb'][parents]
    return prob

def toposort():
    variables = list(bn.keys())
    variables.sort()
    l = []
    while len(l) < len(variables):
        for v in variables:
            if v not in l and all(x in l for x in bn[v]['parents']):
                l.append(v)
    return l

def enum_ask(e, bn, variables):
    x = e.keys()
    X = []
    present = [True if var in x else False for var in variables]
    for i in range (0, len(variables)):
        for var in variables:
            if present[variables.index(var)] != True and any(present[variables.index(c)]==True for c in bn[var]['children']):
                present[variables.index(var)] = True
    for eachNode in variables:
        if present[variables.index(eachNode)] == True:
            X.append(eachNode)
    return enum_all(X, e)

def enum_all(variables, e):
    if len(variables) == 0:
        return 1.0
    Y = variables[0]
    e2 = {}
    if Y in e:
        result = calcProb(bn, Y, e) * enum_all(variables[1:], e)
    else:
        probs = []
        e2 = copy.deepcopy(e)
        for y in [True, False]:
            e2[Y] = y
            probs.append(calcProb(bn, Y, e2) * enum_all(variables[1:], e2))
        result = sum(probs)
    return result

inputs = open(sys.argv[-1], "r").read().strip().splitlines()
queryList = inputs[:inputs.index('******')]
bn = {}
output = open('output.txt', 'w+')
output.close()

i = inputs.index('******')+1
while i < len(inputs):
    if inputs[i][0] != '*':
        if ' | ' in inputs[i]:
            node = inputs[i].split(' | ')[0]
            parents = inputs[i].split(' | ')[1].split(' ')
            prob = -1
            print inputs[i]
            print node
            print parents
            for parent in parents:
                bn[parent]['children'].append(node)
            children = []
            condProb = {} 
            for j in range(i+1,i+1+pow(2, len(parents))):
                valueList = inputs[j].split(' ')
                valueList[1:] = [True if x == '+' else False for x in valueList[1:]]
                condProb[tuple(valueList[1:])] = float(valueList[0])
            i = i+1+pow(2, len(parents))
            bn[node] = {'parents':parents, 'children':children, 'prob':prob, 'condProb':condProb, 'type':'cond'}
        else:
            if inputs[i+1] == 'decision':
                node = inputs[i]
                parents = []
                prob = 1.0
                children = []
                condProb = {}
                bn[node] = {'parents':parents, 'children':children, 'prob':prob, 'condProb':condProb, 'type':'decision'}
                i = i+2
            else:
                node = inputs[i]
                parents = []
                prob = float(inputs[i+1])
                children = []
                condProb = {}
                bn[node] = {'parents':parents, 'children':children, 'prob':prob, 'condProb':condProb, 'type':'cond'}
                i = i+2
    else:
        i = i + 1

variables = toposort()

for query in queryList:
    query = string.replace(query, '+', 'True')
    query = string.replace(query, '-', 'False')
    if query[0] == 'P':
        q = query.split('(')[1][:-1].split(' | ')
        X = q[0]
        e = {}
        if len(q) != 1:
            evidence = q[0].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            p = enum_ask(e, bn, variables)
            e = {}
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            den = enum_ask(e, bn, variables)
            writeToFile(Decimal(str(p/den)).quantize(Decimal('0.01')))
        else:
            evidence = q[0].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            p = enum_ask(e, bn, variables)
            writeToFile(Decimal(str(p)).quantize(Decimal('0.01')))
    elif query[0] == 'E':
        q = query.split('(')[1][:-1].split(' | ')
        e = {}
        if len(q) != 1:
            evidence = q[0].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            e['utility'] = True
            p = enum_ask(e, bn, variables)
            e = {}
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            den = enum_ask(e, bn, variables)
            writeToFile(int(round(p/den)))
        else:
            evidence = q[0].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            e['utility'] = True
            p = enum_ask(e, bn, variables)
            writeToFile(int(round(p)))
    elif query[0] == 'M':
        q = query.split('(')[1][:-1].split(' | ')
        meu = q[0].split(', ')
        perms = list(itertools.product([True, False], repeat = len(meu)))
        p = {}
        den = {}
        e = {}
        if len(q) != 1:
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            e['utility'] = True
            for j in range(0, pow(2, len(meu))):
                for i in range(0, len(meu)):
                    e[meu[i]] = perms[j][i]
                p[perms[j]] = enum_ask(e, bn, variables)
            e = {}
            evidence = q[1].split(', ')
            for evid in evidence:
                if evid.split(' = ')[1] == 'True':
                    e[evid.split(' = ')[0]] = True
                else:
                    e[evid.split(' = ')[0]] = False
            for j in range(0, pow(2, len(meu))):
                for i in range(0, len(meu)):
                    e[meu[i]] = perms[j][i]
                den[perms[j]] = enum_ask(e, bn, variables)
            for key in perms:
                p[key] = int(round(p[key]/den[key]))
            result = ''
            for val in max(p, key=p.get):
                if val == True:
                    result = result + '+ '
                else:
                    result = result + '- '
            writeToFile(result + str(max(p.values())))
        else:
            e['utility'] = True
            for j in range(0, pow(2, len(meu))):
                for i in range(0, len(meu)):
                    e[meu[i]] = perms[j][i]
                p[perms[j]] = int(round(enum_ask(e, bn, variables)))
            result = ''
            for val in max(p, key=p.get):
                if val == True:
                    result = result + '+ '
                else:
                    result = result + '- '
            writeToFile(result + str(max(p.values())))