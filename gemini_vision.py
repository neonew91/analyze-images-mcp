#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
from PIL import Image
import google.generativeai as genai
from IPython.display import display, Markdown
import base64
import requests
from io import BytesIO
from fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("analyzeimage")

# 默认API配置 - 在此处设置你的API密钥和主机地址
DEFAULT_API_KEY = "请替换为你的API密钥"  # 请替换为你的API密钥

def setup_gemini(api_key=None):
    """配置Gemini API"""
    # 使用传入的参数或默认值
    api_key = api_key or DEFAULT_API_KEY
    
    # 配置API
    genai.configure(api_key=api_key)
    
    # 返回模型
    return genai.GenerativeModel(model_name="gemini-2.5-pro-exp-03-25")

def process_image(image_path):
    """处理图片，支持本地路径或URL"""
    if image_path.startswith(('http://', 'https://')):
        response = requests.get(image_path)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_path)
    
    # 显示图片尺寸信息
    print(f"加载图片: {image_path}, 尺寸: {img.size}")
    return img

def process_multiple_images(image_paths):
    """处理多个图片路径或URL，返回图片对象列表"""
    images = []
    for path in image_paths:
        try:
            img = process_image(path)
            images.append(img)
        except Exception as e:
            print(f"处理图片 {path} 时出错: {str(e)}")
    return images

def analyze_images(model, images, user_prompt="请详细描述这些图片中的内容", system_prompt=None):
    """使用Gemini分析多张图片"""
    try:
        if len(images) == 0:
            return "错误: 没有有效的图片可以分析"
            
        # 准备生成内容的请求
        if system_prompt:
            # 使用system prompt和user prompt
            generation_config = {
                "temperature": 0.5,
                "top_p": 0.7,
                "top_k": 32,
                "max_output_tokens": 2048,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            model = genai.GenerativeModel(
                model_name="gemini-pro-vision",
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=system_prompt
            )
        
        # 构建请求内容：先放入提示词，然后放入所有图片
        content = [user_prompt] + images
        
        # 发送API请求，包含提示词和所有图片
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"分析时出错: {str(e)}"

@mcp.tool()
async def analyze_images_feature(urls: list[str]) -> str:
    """分析图片特征
    Args:
        urls: 图片 URL 列表
    """
    # 获取API密钥 - 优先使用命令行参数，其次环境变量，最后使用默认值
    api_key = os.environ.get("GOOGLE_API_KEY") or DEFAULT_API_KEY

    # 设置模型
    model = setup_gemini(api_key)
    images = process_multiple_images(urls)
    if not images:
        return f"图片数据处理异常: 图片数据为空"
    
    anslyz_result = analyze_images(model, images)
    result = f"分析图片结果: {anslyz_result}\n"
    return result


# def main():
#     parser = argparse.ArgumentParser(description="使用Gemini 2.5 Pro进行图片理解")
#     parser.add_argument("--images", nargs='+', required=True, help="图片路径或URL列表，支持多个图片")
#     parser.add_argument("--prompt", default="请详细分析这些图片中的内容，并说明它们之间的关系", help="用户提示词(user prompt)")
#     parser.add_argument("--system_prompt", help="系统提示词(system prompt)")
#     parser.add_argument("--api_key", help="Gemini API密钥 (可选，优先级高于默认值)")
#     args = parser.parse_args()
    
#     # 获取API密钥 - 优先使用命令行参数，其次环境变量，最后使用默认值
#     api_key = args.api_key or os.environ.get("GOOGLE_API_KEY") or DEFAULT_API_KEY
    
#     # 如果API密钥仍然是默认占位符，发出警告
#     if api_key == "YOUR_API_KEY_HERE":
#         print("警告: 你正在使用默认的API密钥占位符。请在脚本中设置正确的API密钥，或通过命令行参数提供。")
    
#     # 设置模型
#     model = setup_gemini(api_key)
    
#     # 处理多张图片
#     print(f"正在处理 {len(args.images)} 张图片...")
#     images = process_multiple_images(args.images)
    
#     if not images:
#         print("错误: 没有成功加载任何图片。请检查图片路径或URL是否正确。")
#         return
    
#     # 分析图片
#     print(f"成功加载 {len(images)} 张图片，正在分析...")
#     print(f"用户提示词: {args.prompt}")
#     if args.system_prompt:
#         print(f"系统提示词: {args.system_prompt}")
    
#     result = analyze_images(model, images, args.prompt, args.system_prompt)
    
#     # 输出结果
#     print("\n分析结果:")
#     print("-" * 50)
#     print(result)
#     print("-" * 50)

if __name__ == "__main__":
    print("启动图片分析MCP服务器...")
    print("请在MCP客户端中配置此服务器")
    mcp.run(transport='stdio')