
import itertools
import logging
import os
from pprint import pformat, pprint
import re
import types


# Variable utilities - mustn't import anything from sloelib except SloeError, SloePlugInManager and SloeUtil
from sloeerror import SloeError
from sloepluginmanager import SloePlugInManager

class SloeVarUtil(object):
    @classmethod
    def process_params(cls, input_string):
        split_list = [""]
        in_double_quotes = False
        in_single_quotes = False
        escape_next = False
        for char in input_string:
            if escape_next:
                # This will excape quotes only
                if char == "n":
                    split_list[-1] += "\n"
                else:
                    split_list[-1] += char
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == "'" and not in_double_quotes:
                split_list[-1] += char
                in_single_quotes = not in_single_quotes
            elif char == '"' and not in_single_quotes:
                split_list[-1] += char
                in_double_quotes = not in_double_quotes
            elif char == "," and not in_double_quotes:
                split_list.append("")
            else:
                split_list[-1] += char
        
        if in_double_quotes or in_double_quotes:
            raise SloeError("Unmatched quotes in |%s|" % input_string)
        if escape_next:
            raise SloeError("Trailing escape charater \\ in |%s|" % input_string)
        
        ret_list = []
        for param in split_list:
            ret_list.append(param.strip())
                
        return ret_list
    
    
    @classmethod
    def command_decode(cls, command_string):
        match = re.match(r'\s*(\w+)\((.*)\)\s*$', command_string)
        if match:
            command_name = match.group(1)
            params = cls.process_params(match.group(2))
            return (command_name, params)
        return (None, None)
 
            
    @classmethod
    def command_execute(cls, command_string, command_name, params):
        varsubst_spec = SloePlugInManager.inst().varsubsts.get(command_name, None)
        if varsubst_spec is None:
            raise SloeError("Cannot substitute string %s (no method %s declared in any plugin)" % (command_string, command_name))

        return SloePlugInManager.inst().call_plugin(
            varsubst_spec["plugin"],
            varsubst_spec["method"],
            params=params)             
            
    
    @classmethod
    def substitute_var_string(cls, input_string, var_substitution_fn):
        command_name, command_params = cls.command_decode(input_string)
        if command_name is not None:
            # Substitute the command name and parameters before executing the command
            subst_params = []
            for param in command_params:
                if len(param) >= 2 and param.startswith('"') and param.endswith('"'):
                    subst_params.append([param[1:-1]]) # Remove string quotes and treat as string literal
                else:
                    subst_params.append(cls.substitute_var_string(param, var_substitution_fn))
                
            return cls.command_execute(input_string, command_name, subst_params)
        
        if var_substitution_fn is None:
            return [input_string]
        else:
            return var_substitution_fn(input_string)

    
    @classmethod
    def substitute_from_node_dict(cls, input_string, node_dict):
        # The var_substitution_fn deals only with replacing single values from the node_dict
        def var_substitution_fn(var_string):
            subst = []
            dot_split = var_string[:].strip().split(".")
            if len(dot_split) >= 2:
                parent_name, field_name = dot_split
                parent_node = node_dict.get(parent_name, None)
                if parent_node is not None:
                    if isinstance(parent_node, types.ListType) or isinstance(parent_node, types.TupleType):
                        for p in parent_node:
                            node_value = p.get(field_name, None)
                            if node_value is not None:
                                subst.append(node_value)
                    else:
                        node_value = parent_node.get(field_name, None)
                        if node_value is not None:
                            subst.append(node_value)
                            
            if len(subst) == 0:
                raise SloeError("No variable %s in '%s'" % (var_string, input_string))
            
            return subst


        ret_str = input_string[:] # Don't overwrite the input string
        # Find string to substitute of the form #{something}
        match_regexp = re.compile(r'(.*)#{([^}]+)}(.*)$', flags=re.DOTALL)
        
        for i in itertools.count():
            if i > 1000:
                raise SloeError("Recursion in variable substitution for %s" % input_string)
            match = match_regexp.match(ret_str)
            if not match:
                break # Exit loop

            ret_str = (match.group(1) +
                     "".join(cls.substitute_var_string(match.group(2), var_substitution_fn)) +
                     match.group(3))

        if ret_str != input_string:
            pass
            # logging.debug("Substituted '%s' for '%s'" % (ret_str, input_string))
        return ret_str.replace("\\n", "\n")
