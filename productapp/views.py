from django.shortcuts import redirect, render
from cart.models import Cart
from category.models import Category, Subcategory
from credentialapp.views import login
from django.contrib import messages
from productapp.models import Product, Productgallery, Sentiment, tbl_Review
from django.db.models import Sum




# Single product View .
def singleproduct(request,id):
    category=Category.objects.all()
    subcategory=Subcategory.objects.all()
    
    review=tbl_Review.objects.filter(product=id)
    count=tbl_Review.objects.filter(product=id).count()
    if "email" in request.session:
        email = request.session['email']
        cart=Cart.objects.filter(user_id=email)
        cart_count=0
        for i in cart:
            cart_count=cart_count+ i.product_qty
        user_review=tbl_Review.objects.filter(user_id=email,product=id)
        rate=tbl_Review.objects.filter(product=id)
        rating=0
        for i in rate:
            rating=rating+ i.rating
        if count == 0:
            total_rate=0.0
        else:
            total_rate=rating / count   
        product=Product.objects.get(id=id)
        category_product=Product.objects.filter(subcategory_id=product.subcategory_id)
        image=Productgallery.objects.filter(product_id=id)
        data={'email':email,
              'total_rate':total_rate,
              'category_product':category_product,
              'count':count,
              'product':product,
              'category':category,
              'subcategory':subcategory,
              'review':review,
              'image':image,
              'user_review':user_review,
              'cart_count':cart_count,
              }
        return render(request,"Customer/single-product.html",data)
    else:
        rate=tbl_Review.objects.filter(product=id)
        rating=0
        for i in rate:
            rating=rating+ i.rating
        if count == 0:
            total_rate=3.0
        else:
            total_rate=rating / count   
        product=Product.objects.get(id=id)
        category_product=Product.objects.filter(subcategory_id=product.subcategory_id)
        image=Productgallery.objects.filter(product_id=id)
        data={'total_rate':total_rate,
              'category_product':category_product,
              'count':count,
              'product':product,
              'category':category,
              'subcategory':subcategory,
              'review':review,
              'image':image
              }
        return render(request,"Customer/singleproduct.html",data)










from textblob import TextBlob

def review(request, id):
    if 'email' in request.session:
        user = request.session['email']
        product = Product.objects.get(id=id)
        if request.method == "POST":
            review = request.POST.get('message')
            rate = request.POST.get('rate')
            custome=float(rate) + float(rate)
            product = Product.objects.get(id=id)

            # Perform sentiment analysis
            blob = TextBlob(review)
            polarity_score = blob.sentiment.polarity
            subjectivity_score = blob.sentiment.subjectivity

            # Get the polarity score for each sentiment
            if polarity_score > 0:
                positive_score = polarity_score
                negative_score = 0
            elif polarity_score < 0:
                positive_score = 0
                negative_score = abs(polarity_score)
            else:
                positive_score = 0
                negative_score = 0
            
            # Save the review and rating to the database
            review = tbl_Review(user_id=user, product_id=product.id,rate=custome, review=review, rating=rate, positive_score=positive_score, negative_score=negative_score)
            review.save()
            
            # Update the sentiment table
            product_rate=0
            reviews = tbl_Review.objects.filter(product_id=id)
            count = reviews.count()
            for i in reviews:
                product_rate=product_rate + i.rate
            product_rate=product_rate/count
            product.rate=product_rate
            product.save()
            positive_avg = 0
            negative_avg = 0

            for i in reviews:
                positive_avg += i.positive_score
                negative_avg += i.negative_score

            # Calculate sentiment scores
            if count > 0:
                positive_avg /= count
                negative_avg /= count

           # Update the sentiment table
            reviews = tbl_Review.objects.filter(product_id=id)
            count = reviews.count()
            positive_avg = 0
            negative_avg = 0
            # neutral_avg=0

            for i in reviews:
                positive_avg=positive_avg + i.positive_score
                negative_avg=negative_avg + i.negative_score
            a=positive_avg/count * 100
            b=negative_avg/count * 100
            sentiment_table=Sentiment.objects.filter(product_id=id)
            if sentiment_table:
                i=Sentiment.objects.get(product_id=id)
                i.num_reviews=count
                i.avg_pos_score=a
                i.avg_neg_score=b
                # i.avg_neu_score=c
                i.save()
            else:
                Sentiment(product_id=id, avg_pos_score=positive_avg, avg_neg_score=negative_avg, num_reviews=count).save()

            return redirect(singleproduct, product.id)
    else:
        return redirect(login)




