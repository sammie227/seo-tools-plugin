import requests
import json
import urllib.parse
from collections.abc import Generator
from typing import Any
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class SeoToolsTool(Tool):
    """5118 SEO元数据生成工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        调用5118 API生成SEO元数据
        
        Args:
            tool_parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 工具调用结果
        """
        # 立即输出确认信息
        yield self.create_text_message(text="🚀 插件开始执行...")
        
        # 输出参数信息
        param_info = f"📋 参数信息：\n{tool_parameters}\n"
        yield self.create_text_message(text=param_info)
        
        # 记录日志
        logger.info("=== 开始执行SEO工具 ===")
        logger.info(f"工具参数: {tool_parameters}")
        
        try:
            # 获取参数
            keywords = tool_parameters.get('keywords', '').strip()
            adverb = tool_parameters.get('adverb', '').strip()
            apikey = tool_parameters.get('apikey', '').strip()
            
            # 输出参数状态
            param_status = f"📋 参数状态：\n- keywords: {keywords}\n- adverb: {adverb}\n- apikey: {'已设置' if apikey else '未设置'}\n"
            yield self.create_text_message(text=param_status)
            
            # 如果没有必要参数，直接返回
            if not keywords or not apikey:
                yield self.create_text_message(text="❌ 错误：缺少必要参数（关键词或API密钥）")
                return
            
            # 开始API调用
            yield self.create_text_message(text="📡 开始调用5118 API...")
            
            # 构建并发送API请求
            api_response = self._call_5118_api(keywords, adverb, apikey)
            
            # 处理API响应
            if api_response['success']:
                formatted_result = self._format_seo_result(api_response['data'])
                yield self.create_text_message(text=formatted_result)
            else:
                yield self.create_text_message(text=api_response['error'])
                
        except Exception as e:
            error_msg = f"🚨 插件执行错误: {str(e)}"
            yield self.create_text_message(text=error_msg)
    
    def _validate_parameters(self, keywords: str, apikey: str) -> str:
        """验证输入参数"""
        if not keywords:
            return "❌ 错误：主关键词不能为空，请输入要优化的关键词"
        
        if len(keywords) > 100:
            return "❌ 错误：主关键词长度不能超过100个字符"
        
        if not apikey:
            return "❌ 错误：API密钥不能为空，请在5118.com获取API密钥"
        
        if len(apikey) < 10:
            return "❌ 错误：API密钥格式不正确，请检查密钥是否完整"
        
        return None
    
    def _call_5118_api(self, keywords: str, adverb: str, apikey: str) -> dict[str, Any]:
        """调用5118 API"""
        try:
            url = "http://apis.5118.com/ai/seometa"
            
            # 构建请求头 - 与PHP示例保持一致
            headers = {
                "Authorization": apikey,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            
            # 构建请求数据 - 与PHP示例保持一致
            data_params = {"keywords": keywords}
            if adverb:
                data_params["adverb"] = adverb
            
            # URL编码数据 - 与PHP示例保持一致
            data = urllib.parse.urlencode(data_params, encoding='utf-8')
            
            # 发送POST请求
            response = requests.post(
                url, 
                headers=headers, 
                data=data,  # 直接传递编码后的字符串
                timeout=30,
                verify=True
            )
            
            # 处理HTTP状态码
            if response.status_code == 200:
                try:
                    result_data = response.json()
                    
                    # 根据5118 API文档检查返回格式
                    if 'errcode' in result_data:
                        if result_data['errcode'] == "0":
                            # 成功
                            return {
                                "success": True, 
                                "data": result_data,
                            }
                        else:
                            # API返回错误
                            error_msg = result_data.get('errmsg', '未知错误')
                            return {
                                "success": False, 
                                "error": f"❌ API错误: {error_msg}",
                            }
                    else:
                        # 没有errcode字段，可能是其他格式
                        return {
                            "success": True, 
                            "data": result_data,
                        }
                        
                except json.JSONDecodeError:
                    # 如果返回的不是JSON，直接返回文本
                    return {
                        "success": True, 
                        "data": {"raw_response": response.text},
                    }
                    
            elif response.status_code == 401:
                return {
                    "success": False, 
                    "error": "❌ API密钥无效或已过期，请检查密钥是否正确",
                }
            elif response.status_code == 403:
                return {
                    "success": False, 
                    "error": "❌ API密钥权限不足，请检查账户余额或权限设置",
                }
            elif response.status_code == 429:
                return {
                    "success": False, 
                    "error": "❌ API调用频率超限，请稍后再试",
                }
            else:
                return {
                    "success": False, 
                    "error": f"❌ API调用失败，状态码: {response.status_code}\n响应: {response.text[:200]}",
                }
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "❌ API请求超时，请检查网络连接或稍后重试"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "❌ 网络连接错误，请检查网络设置"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"❌ 网络请求错误: {str(e)}"}
    
    def _format_seo_result(self, result_data: dict[str, Any]) -> str:
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