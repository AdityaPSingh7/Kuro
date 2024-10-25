# import openai
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt

# # Replace this with your actual OpenAI API key
# OPENAI_API_KEY = "sk-vBpG05CoLJ6RrZRlE_BWXVyO2yCHAF387bmug8AHAbT3BlbkFJNRLjaXq0Y1sQXH1lpniR-ONrSv6vR4CHsB4pwcb3MA"
# openai.api_key = OPENAI_API_KEY

# # Store session-specific conversation history
# chat_sessions = {}

# @csrf_exempt
# def chat_response(request):
#     # Start or get the current session
#     session_id = request.session.session_key
#     if not session_id:
#         request.session.create()
#         session_id = request.session.session_key

#     # If this is the first message, initialize the conversation
#     if 'conversation' not in request.session:
#         request.session['conversation'] = []
#         request.session['user_name'] = None  # Initialize name storage

#     if request.method == "POST":
#         user_message = request.POST.get('message', '').strip()
        
#         # Check if the user introduces their name
#         if "my name is" in user_message.lower():
#             name = user_message.split("my name is")[-1].strip().capitalize()
#             request.session['user_name'] = name  # Store the name in session
#             bot_message = f"Nice to meet you, {name}!"
#         else:
#             # Check if the user's name is stored in session
#             name = request.session.get('user_name')
#             if name and "what's my name" in user_message.lower():
#                 bot_message = f"Your name is {name}!"
#             else:
#                 # Build the conversation prompt
#                 conversation_history = request.session['conversation']
#                 conversation_history.append({"role": "user", "content": user_message})

#                 try:
#                     # Call OpenAI's chat model (using ChatCompletion)
#                     response = openai.ChatCompletion.create(
#                         model="gpt-3.5-turbo",  # Replace with your desired model
#                         messages=[
#                             {"role": "system", "content": "You are a helpful assistant."},
#                             *conversation_history  # Insert previous conversation history
#                         ]
#                     )

#                     bot_message = response['choices'][0]['message']['content'].strip()

#                     # Add bot response to session conversation
#                     conversation_history.append({"role": "assistant", "content": bot_message})
#                     request.session['conversation'] = conversation_history

#                 except Exception as e:
#                     bot_message = f"Error: {str(e)}"

#         return JsonResponse({"response": bot_message})

#     return render(request, 'chat/chat.html')

import openai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Replace with your OpenAI API key
OPENAI_API_KEY = "sk-vBpG05CoLJ6RrZRlE_BWXVyO2yCHAF387bmug8AHAbT3BlbkFJNRLjaXq0Y1sQXH1lpniR-ONrSv6vR4CHsB4pwcb3MA"
openai.api_key = OPENAI_API_KEY

@csrf_exempt
def chat_response(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    if 'conversation' not in request.session:
        request.session['conversation'] = []
        request.session['user_name'] = None

    if request.method == "POST":
        user_message = request.POST.get('message', '').strip()

        if "my name is" in user_message.lower():
            name = user_message.split("my name is")[-1].strip().capitalize()
            request.session['user_name'] = name
            bot_message = f"Nice to meet you, {name}! How are you feeling today?"
        else:
            name = request.session.get('user_name')

            if name and "what's my name" in user_message.lower():
                bot_message = f"Your name is {name}!"
            else:
                # Save conversation
                conversation_history = request.session['conversation']
                conversation_history.append({"role": "user", "content": user_message})

                if "bye" in user_message.lower():
                    # Send conversation to OpenAI API for mental health analysis
                    full_conversation = [
                        {"role": "system", "content": "You are a caring, mature, and empathetic psychiatrist. Your goal is to learn more about the user's life, mental health, and personality. Ask leading and relevant questions about their life and work."}
                    ] + conversation_history

                    try:
                        # Analyze user message sentiment and overall mental health
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=full_conversation
                        )
                        
                        # Get bot response
                        bot_message = response['choices'][0]['message']['content'].strip()
                        
                        # Create a prompt to analyze the overall conversation
                        analysis_prompt = "Based on the following conversation, give a score out of 10 for the user's mental health and highlight key points about their mental health and personality:\n"
                        analysis_prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in full_conversation])
                        
                        # Send analysis prompt to OpenAI
                        analysis_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": "You are a mental health analysis assistant."},
                                      {"role": "user", "content": analysis_prompt}]
                        )
                        
                        # Extract mental health analysis
                        mental_health_analysis = analysis_response['choices'][0]['message']['content'].strip()
                        bot_message += f"\n\n**Mental Health Analysis:** {mental_health_analysis}"

                        # Clear the conversation in session after final response
                        request.session['conversation'] = []
                    except Exception as e:
                        bot_message = f"Error during analysis: {str(e)}"
                else:
                    # Call OpenAI for normal conversation flow
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a caring, mature, and empathetic psychiatrist. Your goal is to learn more about the user's life, mental health, and personality. Ask leading and relevant questions about their life and work."},
                                *conversation_history
                            ]
                        )
                        bot_message = response['choices'][0]['message']['content'].strip()
                    except Exception as e:
                        bot_message = f"Error: {str(e)}"
                
                # Add bot response to conversation
                conversation_history.append({"role": "assistant", "content": bot_message})
                request.session['conversation'] = conversation_history

        return JsonResponse({"response": bot_message})

    return render(request, 'chat/chat.html')
