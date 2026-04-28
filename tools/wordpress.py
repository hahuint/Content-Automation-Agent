from langchain_core.tools import tool
from services.wordpress import WordPressService
from services.pexels import PexelsService

@tool
def publish_to_wordpress(title: str, content: str, image_search_term: str = "", comma_separated_tags: str = "", seo_meta_description: str = "") -> str:
    """
    Publish a blog post to the configured WordPress website.
    Args:
        title: Post title
        content: Full HTML content of the post
        image_search_term: (Optional) Search term for featured image
        comma_separated_tags: (Optional) Tags like "tech,ai"
        seo_meta_description: (Optional) A short meta description
    """
    try:
        print(f"🔍 Finding image for: {image_search_term}")
        image_url = None
        try:
            image_url = PexelsService.get_image_url(image_search_term)
        except Exception as e:
            print(f"⚠️ Could not fetch Pexels image after 3 retries. Skipping image. ({e})")
        
        media_id = None
        if image_url:
            print("☁️ Uploading image to WordPress...")
            try:
                media_id = WordPressService.upload_image(image_url, image_search_term.replace(" ", "_"))
            except Exception as e:
                print(f"⚠️ Could not upload image after 3 retries. Publishing without image. ({e})")

        print("📝 Publishing post to WordPress...")
        response = WordPressService.create_post(title, content, media_id, excerpt=seo_meta_description)
        
        if response.status_code == 201:
            post_url = response.json()['link']
            return f"✅ Post published successfully!\n🔗 {post_url}"
        else:
            return f"❌ Failed to publish. WP Error Code: {response.status_code}. Response: {response.text[:300]}"
            
    except Exception as e:
        return f"❌ Error publishing post: {str(e)}"
