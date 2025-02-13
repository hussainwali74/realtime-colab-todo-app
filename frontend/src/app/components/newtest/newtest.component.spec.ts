import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewtestComponent } from './newtest.component';

describe('NewtestComponent', () => {
  let component: NewtestComponent;
  let fixture: ComponentFixture<NewtestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewtestComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewtestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
