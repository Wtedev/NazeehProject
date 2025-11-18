import streamlit as st

st.set_page_config(page_title="المساعد القانوني السعودي", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

def select_chat(index):
    st.session_state.selected_chat = index

left, middle, right = st.columns([1, 0.05, 4])

with left:
    st.header("الأسئلة السابقة")

    if len(st.session_state.history) == 0:
        st.info("..لا يوجد أسئلة بعد")
    else:
        for i, chat in enumerate(st.session_state.history):
            if st.button(chat["question"], key=f"chat_{i}", use_container_width=True):
                select_chat(i)


with middle:
    st.markdown(
        """
        <div style="border-left:2px solid #ddd; height:100%; margin:0 10px;"></div>
        """,
        unsafe_allow_html=True
    )


with right:
    st.title(" ️ ️ ⚖️️ مُـساعـدك القـانوني السـعـودي ")
    st.markdown(
        "خِـدمة تقدم إجابات دقيقة تستند إلى الأنظمة السعودية ، وفر وقتك و زد  وعيك القانوني "
    )

    if st.session_state.selected_chat is None:
        user_q = st.text_input("",
            placeholder=" : اكتب سؤالك القانوني هنا"
        )

        st.caption("ملاحظة: هذا البوت يستخدم لأغراض التوعية القانونية ولا يُغني عن استشارة محامي مختص ")

        if st.button("ارسل سؤالك"):
            if user_q.strip() == "":
                st.warning(" !! اكتب سؤال أولاً ")
            else:
                answer = f"هذه إجابة تجريبية للسؤال:\n\n{user_q}\n\n(هنا الرد الحقيقي + نص المادة القانونية)"

                st.session_state.history.append({
                    "question": user_q,
                    "answer": answer
                })

                st.write(" الإجابة:")
                st.write(answer)
    else:
        chat = st.session_state.history[st.session_state.selected_chat]

        st.subheader(" :  سؤالك وإجابته القانونية القانوني ")
        st.write(chat["answer"])

        if st.button("رجوع للأسئلة الجديدة"):
            st.session_state.selected_chat = None
