def build_context(activities):
     context=""

     for activity in activities:
          (
            activity_id,
           timestamp,
           app_name,
           window_title,
           ocr_text,
           category,
           source
           )=activity
          
          context+=(
               f"Time: {timestamp}\n"
               f"App: {app_name}\n"
               f"Window: {window_title}\n"
          )

          if ocr_text:
               context+=(
                    f"OCR:\n{ocr_text}"
               )

          context+="\n"
          context+="-"*50
          context+="\n\n"

     return context 

