# -*- coding: utf-8 -*-

"""
###只针对注册域名###
1)根据自定义的域名字符串相似性原则判断两个域名字符串是否相似
2)将相似的规则提取成枚举模式
"""
import sys
from tldextract import extract

class Domains_Match():
    """
    1)根据自定义的域名字符串相似性原则判断两个域名字符串是否相似
    2)将相似的规则提取成枚举模式
    """
    def delete_match(self,long_str,short_str):
        """
        对长度相差一的域名对进行匹配
        :param long_str: 
        :param short_str: 
        :return: 
        """
        if len(long_str)-len(short_str)!=1:
            sys.exit(-1)
        idx = -1
        s = ''
        for i, r in enumerate(zip(long_str[:-1], short_str)):
            ch1, ch2 = r
            if ch1 == ch2:
                s+=ch1
            else:
                idx = i
                break

        if idx == -1 or s+''.join(list(long_str)[idx+1:])==short_str:
            return 1
        else:
            return 0

    def select_symbol(self,c1,c2):

        if c1.isdigit() and c2.isdigit():
            return '#'
        elif c1.isalpha() and c2.isalpha():
            return '*'
        else:
            return '$'

    def short_match(self,str1,str2):
        """
        第一个字符不等
        短字符匹配 长度小于３
        :param str1: 
        :param str2: 
        :return: 
        """
        if len(str1)==2:
            if str1[1]==str2[1]:
                return self.select_symbol(str1[0], str2[0])+str1[1]
            else:
                return self.select_symbol(str1[0], str2[0])+self.select_symbol(str1[1], str2[1])
        else:
            return self.select_symbol(str1[0], str2[0])

    def jump_match(self,str1,str2,i):
        """
        第i个元素不等
        :param i: 
        :return: 
        """
        b = str2[i]
        mode = list(str1)
        new_str = list(str1)
        idx_list = []
        count = 0
        for j,r in enumerate(zip(str1[i:],str2[i:])):
            if r[0]!=r[1]:
                count+=1
                idx_list.append(i+j)
        a_list = set()
        b_list = set()
        for j in idx_list:
            a_list.add(str1[j])
            b_list.add(str2[j])
            mode[j] = self.select_symbol(str1[j],str2[j])
            new_str[j] = b

        if count>=3:
            if len(a_list)==1 and len(b_list)==1 and ''.join(new_str)==str2:
                flag = 1
                mode = ''.join(mode)+'&'
            else:
                flag = 0
                mode = str1
        elif count == 2:
            flag = 1
            if len(a_list)==1 and len(b_list)==1 and ''.join(new_str)==str2:
                mode = ''.join(mode)+'&'
            else:
                mode = ''.join(mode)
        else:
            flag = 1
            mode = ''.join(mode)

        return flag,mode

    def match(self,domain1,domain2):
        """
        &:连续指示符
        #:数字通配符
        *:字母通配符
        $:数字/字母通配符
        %:顶级域通配符
        :param domain1: 
        :param domain2: 
        :return: 
        """
        flag = 0
        mode = domain1
        if domain1 == domain2:
            sys.exit(-1)
        else:
            str1 = extract(domain1)
            str2 = extract(domain2)
            if str1.suffix!=str2.suffix:
                if str1.domain == str2.domain:
                    flag = 1
                    mode = str1.domain+'.%'#枚举顶级域
            else:
                if len(str1.domain)-len(str2.domain)==0:
                    idx = -1
                    prefix = ''
                    for i, r in enumerate(zip(str1.domain, str2.domain)):
                        if r[0] != r[1]:
                            idx = i
                            break
                        else:
                            prefix += r[0]
                    flag,mode = self.jump_match(str1.domain,str2.domain,idx)
                    if flag:
                        mode = mode+'.'+str1.suffix

            return flag,mode

if  __name__ == "__main__":
    print Domains_Match().match('000x38.com', '000a38.com')
    print Domains_Match().match('0000524.com','00001524.com')
    print Domains_Match().match('00111524.com', '00221524.com')
    print Domains_Match().match('00aaa1524.com', '00bbb1524.com')
    print Domains_Match().match('2020504.com', '0020524.com')