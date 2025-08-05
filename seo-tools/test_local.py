#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5118 API 本地测试脚本
用于验证API调用是否正常工作
"""

import requests
import urllib.parse
import json
import sys

def test_5118_api(apikey, keywords, adverb=""):
    """
    测试5118 API调用
    
    Args:
        apikey: 5118 API密钥
        keywords: 主关键词
        adverb: 副关键词（可选）
    
    Returns:
        dict: API响应结果
    """
    try:
        url = "http://apis.5118.com/ai/seometa"
        
        # 构建请求头
        headers = {
            "Authorization": apikey,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        # 构建请求数据
        data_params = {"keywords": keywords}
        if adverb:
            data_params["adverb"] = adverb
        
        # URL编码数据
        data = urllib.parse.urlencode(data_params, encoding='utf-8')
        
        print(f"🔍 测试信息:")
        print(f"   URL: {url}")
        print(f"   主关键词: {keywords}")
        print(f"   副关键词: {adverb if adverb else '无'}")
        print(f"   API密钥长度: {len(apikey)}")
        print()
        
        # 发送POST请求
        print("📡 发送API请求...")
        response = requests.post(
            url, 
            headers=headers, 
            data=data,
            timeout=30,
            verify=True
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        # 处理HTTP状态码
        if response.status_code == 200:
            try:
                result_data = response.json()
                print(f"📊 JSON响应: {json.dumps(result_data, ensure_ascii=False, indent=2)}")
                
                # 根据5118 API文档检查返回格式
                if 'errcode' in result_data:
                    if result_data['errcode'] == "0":
                        print("✅ API调用成功!")
                        return {
                            "success": True, 
                            "data": result_data,
                        }
                    else:
                        # API返回错误
                        error_msg = result_data.get('errmsg', '未知错误')
                        print(f"❌ API错误: {error_msg}")
                        return {
                            "success": False, 
                            "error": f"❌ API错误: {error_msg}",
                        }
                else:
                    # 没有errcode字段，可能是其他格式
                    print("⚠️ 响应格式异常，但状态码正常")
                    return {
                        "success": True, 
                        "data": result_data,
                    }
                    
            except json.JSONDecodeError:
                # 如果返回的不是JSON，直接返回文本
                print(f"⚠️ 响应不是JSON格式: {response.text}")
                return {
                    "success": True, 
                    "data": {"raw_response": response.text},
                }
                
        elif response.status_code == 401:
            print("❌ API密钥无效或已过期")
            return {
                "success": False, 
                "error": "❌ API密钥无效或已过期，请检查密钥是否正确",
            }
        elif response.status_code == 403:
            print("❌ API密钥权限不足")
            return {
                "success": False, 
                "error": "❌ API密钥权限不足，请检查账户余额或权限设置",
            }
        elif response.status_code == 429:
            print("❌ API调用频率超限")
            return {
                "success": False, 
                "error": "❌ API调用频率超限，请稍后再试",
            }
        else:
            print(f"❌ API调用失败，状态码: {response.status_code}")
            print(f"❌ 响应内容: {response.text[:200]}")
            return {
                "success": False, 
                "error": f"❌ API调用失败，状态码: {response.status_code}\n响应: {response.text[:200]}",
            }
            
    except requests.exceptions.Timeout:
        print("❌ API请求超时")
        return {"success": False, "error": "❌ API请求超时，请检查网络连接或稍后重试"}
    except requests.exceptions.ConnectionError:
        print("❌ 网络连接错误")
        return {"success": False, "error": "❌ 网络连接错误，请检查网络设置"}
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {str(e)}")
        return {"success": False, "error": f"❌ 网络请求错误: {str(e)}"}

def format_seo_result(result_data):
    """格式化SEO结果输出"""
    if not result_data:
        return "❌ API返回数据为空"
    
    # 如果是原始响应
    if 'raw_response' in result_data:
        return f"📊 5118 SEO元数据生成结果：\n\n{result_data['raw_response']}"
    
    # 格式化JSON响应
    formatted_output = ["🎯 5118 SEO元数据生成结果", "=" * 40, ""]
    
    # 根据5118 API的实际响应结构来格式化
    if isinstance(result_data, dict):
        # 检查是否有errcode和data字段（5118 API标准格式）
        if 'errcode' in result_data and 'data' in result_data:
            if result_data['errcode'] == "0":
                # 成功，解析data字段
                data_content = result_data['data']
                formatted_output.extend([
                    "📝 SEO元数据:",
                    f"   {data_content}",
                    ""
                ])
            else:
                # 有错误
                error_msg = result_data.get('errmsg', '未知错误')
                formatted_output.extend([
                    "❌ API错误:",
                    f"   错误代码: {result_data['errcode']}",
                    f"   错误信息: {error_msg}",
                    ""
                ])
        else:
            # 其他格式，显示所有字段
            for key, value in result_data.items():
                if value:
                    formatted_output.extend([
                        f"📌 {key}:",
                        f"   {value}",
                        ""
                    ])
    else:
        # 如果不是字典格式，直接显示
        formatted_output.append(str(result_data))
    
    formatted_output.extend(["", "✅ SEO元数据生成完成！"])
    
    return "\n".join(formatted_output)

def main():
    """主函数"""
    print("🚀 5118 API 本地测试工具")
    print("=" * 50)
    
    # 获取用户输入
    print("\n请输入测试信息:")
    apikey = input("🔑 5118 API密钥: ").strip()
    keywords = input("🎯 主关键词: ").strip()
    adverb = input("📝 副关键词 (可选，直接回车跳过): ").strip()
    
    if not apikey:
        print("❌ 错误：API密钥不能为空")
        return
    
    if not keywords:
        print("❌ 错误：主关键词不能为空")
        return
    
    print("\n" + "=" * 50)
    
    # 测试API调用
    result = test_5118_api(apikey, keywords, adverb)
    
    print("\n" + "=" * 50)
    print("📋 测试结果:")
    print("=" * 50)
    
    if result['success']:
        formatted_result = format_seo_result(result['data'])
        print(formatted_result)
    else:
        print(result['error'])

if __name__ == "__main__":
    main() 