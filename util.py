
def check_collision(rect, rect_list):
    for i in rect_list:
        if(rect.colliderect(i)):
            return True
    
    return False