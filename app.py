import streamlit as st
import tempfile
import os
from PIL import Image
import pandas as pd
from deepface import DeepFace
import plotly.express as px

# Configure the page
st.set_page_config(
    page_title="Face Analysis App",
    page_icon="🎯",
    layout="wide"
)

# Simple CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
    }
    
    .info-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #3498db;
    }
    
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .section-header {
        font-size: 1.3rem;
        color: #34495e;
        font-weight: 500;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location and return the path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def display_analysis_results(results):
    """Display facial analysis results in a clean, simple format"""
    if isinstance(results, list) and len(results) > 0:
        result = results[0]  # Take the first face detected
        
        # Demographics Section
        st.markdown('<h3 class="section-header">Personal Information</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = result.get('age', 'Unknown')
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #3498db; margin: 0;">Age</h4>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{age} years</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            gender = result.get('dominant_gender', 'Unknown')
            gender_conf = result.get('gender', {}).get(gender.lower(), 0) if result.get('gender') else 0
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #e74c3c; margin: 0;">Gender</h4>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{gender}</p>
                <p style="font-size: 0.9rem; color: #7f8c8d; margin: 0;">{gender_conf:.1f}% confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            race = result.get('dominant_race', 'Unknown')
            race_conf = result.get('race', {}).get(race.lower(), 0) if result.get('race') else 0
            st.markdown(f"""
            <div class="metric-container">
                <h4 style="color: #f39c12; margin: 0;">Ethnicity</h4>
                <p style="font-size: 1.5rem; font-weight: bold; margin: 5px 0;">{race}</p>
                <p style="font-size: 0.9rem; color: #7f8c8d; margin: 0;">{race_conf:.1f}% confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Emotion Analysis Section
        st.markdown('<h3 class="section-header">Emotion Analysis</h3>', unsafe_allow_html=True)
        
        emotions = result.get('emotion', {})
        if emotions:
            # Get dominant emotion
            dominant_emotion = max(emotions, key=emotions.get)
            dominant_confidence = emotions[dominant_emotion]
            
            st.info(f"**Dominant Emotion:** {dominant_emotion.title()} ({dominant_confidence:.1f}%)")
            
            # Simple emotion chart
            emotion_df = pd.DataFrame(list(emotions.items()), columns=['Emotion', 'Confidence'])
            emotion_df = emotion_df.sort_values('Confidence', ascending=False)
            
            # Display emotions as metrics
            cols = st.columns(len(emotions))
            for i, (emotion, confidence) in enumerate(emotion_df.values):
                with cols[i]:
                    st.metric(emotion.title(), f"{confidence:.1f}%")
            
            # Simple bar chart
            fig = px.bar(emotion_df, 
                        x='Emotion', 
                        y='Confidence',
                        title="Emotion Confidence Levels",
                        color='Confidence',
                        color_continuous_scale='Blues')
            
            fig.update_layout(
                height=400,
                xaxis_title="Emotions",
                yaxis_title="Confidence (%)",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Data Section
        st.markdown('<h3 class="section-header">Detailed Results</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'gender' in result:
                st.markdown("**Gender Distribution**")
                gender_data = result['gender']
                gender_df = pd.DataFrame(list(gender_data.items()), columns=['Gender', 'Confidence'])
                st.dataframe(gender_df, hide_index=True, use_container_width=True)
        
        with col2:
            if 'race' in result:
                st.markdown("**Ethnicity Distribution**")
                race_data = result['race']
                race_df = pd.DataFrame(list(race_data.items()), columns=['Ethnicity', 'Confidence'])
                race_df = race_df.sort_values('Confidence', ascending=False)
                st.dataframe(race_df, hide_index=True, use_container_width=True)
            
    else:
        st.error("No face detected in the image. Please upload an image with a clear, visible face.")

def main():
    # Main header
    st.markdown('<h1 class="main-header">Face Analysis App</h1>', unsafe_allow_html=True)
    
    # Information section
    st.markdown("""
    <div class="info-section">
        <h4>How it works:</h4>
        <p>Upload an image with a clear face and our AI will analyze:</p>
        <ul>
            <li><strong>Age estimation</strong> - Predicts the person's age</li>
            <li><strong>Gender detection</strong> - Identifies gender with confidence levels</li>
            <li><strong>Ethnicity analysis</strong> - Determines ethnic background</li>
            <li><strong>Emotion recognition</strong> - Detects current emotional state</li>
        </ul>
        <p><em>All processing is done locally and images are not stored.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section
    st.markdown("### Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image file", 
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo with a visible face for best results"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Analysis button
            if st.button("Analyze Face", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    try:
                        # Save uploaded file
                        img_path = save_uploaded_file(uploaded_file)
                        
                        if img_path:
                            # Perform face analysis
                            results = DeepFace.analyze(
                                img_path=img_path, 
                                actions=['age', 'gender', 'race', 'emotion'],
                                enforce_detection=False
                            )
                            
                            # Display results
                            with col2:
                                display_analysis_results(results)
                            
                            # Cleanup temporary file
                            os.unlink(img_path)
                            
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        st.info("Please try with a different image or ensure the face is clearly visible.")
        
        with col2:
            if 'results' not in locals():
                st.markdown("""
                <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 10px;">
                    <h4 style="color: #6c757d;">Ready for Analysis</h4>
                    <p style="color: #6c757d;">Click 'Analyze Face' to get detailed insights about the uploaded image.</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
